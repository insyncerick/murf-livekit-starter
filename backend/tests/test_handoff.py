import asyncio
import sys
import os
from unittest.mock import MagicMock

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend/src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import Assistant, ReturnsSpecialistAgent
from returns_db import init_returns_db, get_order, create_return_ticket

async def test_handoff_workflow():
    print("\n--- TEST 1: Database and Specialist Tool Verification ---")
    init_returns_db()
    order = get_order("ORD-1001")
    assert order is not None, "ORD-1001 should exist in returns db"
    print(f"[PASS] Found Order ORD-1001: {order['items']} (Total: Rs. {order['total_amount']})")

    specialist = ReturnsSpecialistAgent(
        user_id="tilak",
        caller_name="Tilak",
        handoff_reason="damaged milk packet",
        handoff_order_id="ORD-1001",
        item_summary="Amul Taaza Milk (500ml)",
    )
    print("[PASS] Specialist instantiated with instructions including context:")
    assert "damaged milk packet" in specialist.instructions
    assert "ORD-1001" in specialist.instructions
    assert "Tilak" in specialist.instructions

    # Test specialist tools using mocked context
    mock_ctx = MagicMock()
    lookup_res = await specialist.lookup_order_for_return(mock_ctx, order_id="ORD-1001")
    print(f"[PASS] Specialist lookup_order_for_return result: {lookup_res['status']}, items={lookup_res['items']}")

    ticket = await specialist.process_refund_ticket(
        mock_ctx,
        order_id="ORD-1001",
        items="Amul Taaza Milk (500ml)",
        reason="damaged milk packet leaking",
        refund_amount=60.0,
    )
    print(f"[PASS] Specialist process_refund_ticket result: Return ID {ticket['return_id']}, status={ticket['status']}")

    print("\n--- TEST 2: Main Agent Handoff Tool Execution ---")
    main_agent = Assistant(user_id="tilak", call_id="test-room-123")
    
    # Simulate handoff call by LLM
    handoff_result = await main_agent.handoff_to_returns_specialist(
        mock_ctx,
        reason="leaking milk packet received yesterday",
        order_id="ORD-1001",
        item_summary="Amul Taaza Milk",
    )
    assert isinstance(handoff_result, ReturnsSpecialistAgent), "Handoff tool must return ReturnsSpecialistAgent instance"
    print(f"[PASS] Main agent successfully executed handoff and returned specialist instance: {type(handoff_result).__name__}")
    print("[PASS] Verification complete! All tests passed successfully.")

if __name__ == "__main__":
    asyncio.run(test_handoff_workflow())
