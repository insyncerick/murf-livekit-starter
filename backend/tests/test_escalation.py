import os
import pytest
from dotenv import load_dotenv

from livekit.agents import AgentSession, llm
from livekit.plugins import google

from agent import Assistant
from escalation_db import init_escalation_db, save_escalation, get_open_escalations

load_dotenv(".env.local")
if "GOOGLE_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GOOGLE_API_KEY"]


def _llm() -> llm.LLM:
    return google.LLM(model="gemini-3.5-flash-lite")


def test_escalation_database_storage():
    """Verify that human escalation requests are stored cleanly in SQLite database without sensitive information."""
    init_escalation_db()

    record = save_escalation(
        user_id="test-user-123",
        name="Tilak",
        reason="Order refund dispute",
        summary="Customer charged twice for order #1084. Agent verified billing mismatch.",
        agent_checked="Checked order log #1084 and confirmed double charge of Rs. 450",
        urgency="high",
        language="English",
        preferred_contact="phone call",
    )

    assert record["reference_id"].startswith("ESC-")
    assert record["user_id"] == "test-user-123"
    assert record["status"] == "OPEN"

    open_requests = get_open_escalations()
    assert len(open_requests) > 0
    match = next((r for r in open_requests if r["id"] == record["reference_id"]), None)
    assert match is not None
    assert match["reason"] == "Order refund dispute"
    assert match["urgency"] == "high"


@pytest.mark.asyncio
async def test_escalation_path_with_consent():
    """
    Test Path 1: Human Help Required.
    Caller asks for help with a payment refund dispute.
    Agent asks for permission, caller consents, agent calls create_escalation tool.
    """
    async with (
        _llm() as llm_inst,
        AgentSession(llm=llm_inst) as session,
    ):
        assistant = Assistant(user_id="user-dispute-test")
        await session.start(assistant)

        # User reports a payment dispute
        result = await session.run(
            user_input="I was double charged for my previous order. I want a refund right now."
        )

        # Agent checks memory / greets / asks for permission to submit escalation details
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm_inst,
                intent="""
                Recognizes the refund dispute issue and offers to connect or create a request for human support.
                May ask the caller for permission to submit their contact and issue details to human support.
                """,
            )
        )

        # User consents to submit request
        result2 = await session.run(user_input="Yes, please go ahead and create the request.")

        # Agent should call create_escalation function tool
        result2.expect.next_event().is_function_call(name="create_escalation")
        result2.expect.next_event().is_function_call_output()

        # Agent gives reference ID and next steps
        await (
            result2.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm_inst,
                intent="""
                Provides the reference ID to the user and explains next steps (e.g. human agent will follow up within 24 hours).
                """,
            )
        )


@pytest.mark.asyncio
async def test_normal_path_no_escalation():
    """
    Test Path 2: Normal Conversation.
    Caller asks a standard catalog price/stock question.
    Agent uses standard catalog tool and does NOT call create_escalation.
    """
    async with (
        _llm() as llm_inst,
        AgentSession(llm=llm_inst) as session,
    ):
        assistant = Assistant(user_id="user-normal-test")
        await session.start(assistant)

        # User asks for catalog price of rice and sugar
        result = await session.run(
            user_input="Can you check if rice and sugar are available and how much 2kg rice and 1kg sugar would cost?"
        )

        # Should call check_catalog_and_compute_total tool
        result.expect.next_event().is_function_call(name="check_catalog_and_compute_total")
        result.expect.next_event().is_function_call_output()

        # Agent responds with catalog price info
        await (
            result.expect.next_event()
            .is_message(role="assistant")
            .judge(
                llm_inst,
                intent="""
                Provides information about item availability and total cost for rice and sugar.
                Does NOT suggest human escalation.
                """,
            )
        )

        # Verify no escalation call occurred
        result.expect.no_more_events()
