import logging
import asyncio

from dotenv import load_dotenv

from livekit import rtc
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    RunContext,
    cli,
    function_tool,
    room_io,
    tokenize,
)

from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from prompt import SYSTEM_PROMPT
from user_db import init_db, get_user, save_user


logger = logging.getLogger("agent")

load_dotenv(".env.local")


# =========================================================
# DATABASE
# =========================================================

init_db()


# =========================================================
# ASSISTANT
# =========================================================

class Assistant(Agent):

    def __init__(self, user_id: str) -> None:
        """
        Initialize the Assistant agent.
        Parameters:
          user_id: Stable identifier for the caller.
        """
        instructions = SYSTEM_PROMPT + """

        IMPORTANT MEMORY BEHAVIOR

        At the beginning of every call:

        1. You MUST use the lookup_user tool to check whether this caller
            already has saved information.

        2. If lookup_user returns a saved name:
            - Do NOT ask for the caller's name again.
            - Greet the caller using their saved name.
            - Example:
              "Hi Tilak, welcome back! How can I help you today?"

        3. If lookup_user returns no saved information:
            - Treat the caller as a new caller.
            - Ask for their name naturally when appropriate.

        4. When the caller gives their name or other useful information,
            DO NOT immediately save it.

        5. First ask for permission.

            Example:
            "Would you like me to remember your name for your future calls?"

        6. Only if the caller clearly agrees with words such as:
            "yes", "sure", "okay", "you can remember", or similar,
            use the save_user_memory tool.

        7. If the caller says no, do NOT use save_user_memory.

        8. Never tell the caller that information was saved unless the
            save_user_memory tool actually reports successful saving.

        LOCAL COMMERCE MEMORY

        Useful information that may be saved after consent includes:
        - caller name
        - language preference
        - past orders
        - usual product quantities
        - preferred delivery time/slot

        IMPORTANT:
        Do not invent any information.
        Only save information that the caller actually provided.

        RETURNING CALLER BEHAVIOR

        If the database contains the caller's name:

        Do NOT say:
        "What is your name?"

        Instead say something natural such as:
        "Hi Tilak, welcome back! How can I help you today?"

        If useful saved facts exist, you may naturally refer to them.

        Example:
        "Hi Tilak, welcome back! Would you like help with your usual order?"

        Do not reveal the internal user ID or database details to the caller.
        
        #---BEGIN CACHED USER---
        {{cached_user_name}}
        #---END CACHED USER---
        """

        super().__init__(instructions=instructions)

        # Stable caller identity
        self._user_id = user_id
        # Pre-load any existing user data so the LLM can reference it immediately
        self._cached_user: dict = {}

    async def _populate_cached_user(self) -> None:
        """
        Populate `self._cached_user` by invoking the `lookup_user` tool.
        """
        try:
            self._cached_user = await self.lookup_user(RunContext())
        except Exception as exc:
            logger.error(f"Failed to pre-load user memory: {exc}")
            self._cached_user = {}

    async def start(self, *args, **kwargs):
        # Load user data synchronously before starting session
        self._cached_user = await self.lookup_user(RunContext())
        cached_name = self._cached_user.get("name", "")
        self.instructions = self.instructions.replace(
            "{{cached_user_name}}", f"Saved name: {cached_name}"
        )
        return await super().start(*args, **kwargs)

    # =====================================================
    # TOOL 1 — LOOK UP CALLER
    # =====================================================

    @function_tool
    async def lookup_user(self, context: RunContext) -> dict:
        """
        Look up the current caller in the SQLite database.

        Always use this at the beginning of a call to determine
        whether the caller has spoken with Bazaar Mitra before.
        """

        logger.info(
            f"LOOKUP USER → user_id={self._user_id}"
        )

        user = get_user(self._user_id)

        if user:

            logger.info(
                f"MEMORY FOUND → "
                f"user_id={self._user_id}, "
                f"name={user.get('name')}, "
                f"facts={user.get('facts')}"
            )

            return user

        logger.info(
            f"NEW USER → no memory found for "
            f"user_id={self._user_id}"
        )

        return {}


    # =====================================================
    # TOOL 2 — SAVE CALLER MEMORY
    # =====================================================

    @function_tool
    async def save_user_memory(
        self,
        context: RunContext,
        name: str,
        language_preference: str = "",
        facts: dict | None = None,
    ) -> str:
        """
        Save caller information to SQLite.

        IMPORTANT:
        This tool must ONLY be used after the caller has explicitly
        given permission to remember their information.
        """

        logger.info(
            f"SAVE MEMORY REQUEST → "
            f"user_id={self._user_id}, "
            f"name={name}, "
            f"facts={facts}"
        )

        # Get existing information
        existing_user = get_user(self._user_id)

        existing_facts = {}

        if existing_user:
            existing_facts = existing_user.get("facts", {})

        # Merge old and new facts
        if facts:
            existing_facts.update(facts)

        # Keep old name if no new name was supplied
        final_name = name

        if not final_name and existing_user:
            final_name = existing_user.get("name", "")

        # Keep old language if no new language was supplied
        final_language = language_preference

        if not final_language and existing_user:
            final_language = existing_user.get(
                "language_preference",
                ""
            )

        # Save to database
        success = save_user(
            user_id=self._user_id,
            name=final_name,
            language_preference=final_language,
            facts=existing_facts,
        )

        if success:

            logger.info(
                f"MEMORY SAVED SUCCESSFULLY → "
                f"user_id={self._user_id}, "
                f"name={final_name}, "
                f"facts={existing_facts}"
            )

            return "Caller information was saved successfully."

        logger.error(
            f"MEMORY SAVE FAILED → "
            f"user_id={self._user_id}"
        )

        return "The caller information could not be saved."


# =========================================================
# LIVEKIT SERVER
# =========================================================

server = AgentServer()


# =========================================================
# PREWARM
# =========================================================

def prewarm(proc: JobProcess):

    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


# =========================================================
# AGENT SESSION
# =========================================================

@server.rtc_session(agent_name="my-agent")
async def my_agent(ctx: JobContext):

    # Logging
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }


    # -----------------------------------------------------
    # CONNECT TO ROOM
    # -----------------------------------------------------

    await ctx.connect()


    # -----------------------------------------------------
    # WAIT FOR CALLER
    # -----------------------------------------------------

    participant = await ctx.wait_for_participant()

    user_id = participant.identity

    logger.info(
        f"USER ID → {user_id}"
    )


    # -----------------------------------------------------
    # DEBUG: CHECK DATABASE DIRECTLY
    # -----------------------------------------------------

    existing_user = get_user(user_id)

    if existing_user:

        logger.info(
            f"DATABASE CHECK → RETURNING USER: "
            f"{existing_user.get('name')}"
        )

    else:

        logger.info(
            "DATABASE CHECK → NEW USER"
        )


    # -----------------------------------------------------
    # VOICE SESSION
    # -----------------------------------------------------

    session = AgentSession(

        # Speech to Text
        stt=deepgram.STT(
            model="nova-3"
        ),

        # LLM
        llm=google.LLM(
            model="gemini-3.5-flash-lite",
        ),

        # Text to Speech
        tts=murf.TTS(
            voice="en-In-anusha",
            style="Conversation",
            tokenizer=tokenize.basic.SentenceTokenizer(
                min_sentence_len=2
            ),
            text_pacing=True,
        ),

        # Turn Detection
        turn_detection=MultilingualModel(),

        # Voice Activity Detection
        vad=ctx.proc.userdata["vad"],

        # Generate response early
        preemptive_generation=True,
    )


    # -----------------------------------------------------
    # START SESSION
    # -----------------------------------------------------

    await session.start(

        agent=Assistant(
            user_id=user_id
        ),

        room=ctx.room,

        room_options=room_io.RoomOptions(

            audio_input=room_io.AudioInputOptions(

                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC()
                ),

            ),

        ),

    )


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":
    cli.run_app(server)
