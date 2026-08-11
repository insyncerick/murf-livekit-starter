import asyncio
import os
import uuid
import logging
from dotenv import load_dotenv
from livekit import api
from pathlib import Path

# Load .env.local from this directory
env_path = Path(__file__).parent.parent / ".env.local"
load_dotenv(env_path)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("outbound")

async def main():
    sip_host = os.getenv("SIP_OUTBOUND_HOST")
    sip_trunk_id = os.getenv("SIP_TRUNK_ID")
    livekit_url = os.getenv("LIVEKIT_URL")
    livekit_api_key = os.getenv("LIVEKIT_API_KEY")
    livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    # FETCH DESTINATION FROM ENV
    destination_sip_uri = os.getenv("DESTINATION_SIP_URI")

    if not all([sip_host, livekit_url, livekit_api_key, livekit_api_secret, destination_sip_uri]):
        logger.error("Missing required environment variables. Please check .env.local")
        return

    # In LiveKit, you need a room for the SIP participant and the agent to join
    room_name = f"outbound-call-{uuid.uuid4().hex[:8]}"
    logger.info(f"Initiating outbound call to {destination_sip_uri} in room {room_name}")

    # Use the LiveKit API to create a SIP participant
    client = api.LiveKitAPI(livekit_url, livekit_api_key, livekit_api_secret)
    
    try:
        # Note: You must have a SIP trunk configured in your LiveKit project
        # This will instruct LiveKit to dial the SIP URI and place the call into the room
        request = api.CreateSIPParticipantRequest(
            sip_trunk_id=sip_trunk_id or "",
            # USE VARIABLE INSTEAD OF HARDCODED STRING
            sip_call_to=os.getenv("SIP_USERNAME"),
            room_name=room_name,
            participant_identity=f"sip-{uuid.uuid4().hex[:8]}",
            participant_name="Customer",
        )
        
        await client.sip.create_sip_participant(request)
        logger.info(f"Outbound SIP call initiated successfully! The agent should connect to room '{room_name}'")
        
    except Exception as e:
        logger.error(f"Failed to initiate outbound SIP call: {e}")
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(main())
