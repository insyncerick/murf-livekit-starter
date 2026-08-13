import os
import tempfile
import pytest
from calls_db import init_calls_db, record_call_start, mark_call_success, finalize_call, get_call_stats


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp:
        db_path = tmp.name
    init_calls_db(db_path)
    yield db_path
    if os.path.exists(db_path):
        os.remove(db_path)


def test_call_lifecycle_success(temp_db):
    """Test recording a call that completes a product enquiry (SUCCESS condition)."""
    call_id = "room-test-101"
    user_id = "caller-alice"

    # Step 1: Start call (defaults to FAILED until success criteria met)
    start_rec = record_call_start(call_id=call_id, user_id=user_id, db_path=temp_db)
    assert start_rec["call_id"] == call_id
    assert start_rec["status"] == "FAILED"

    # Step 2: Mark call as successful when enquiry completes
    updated = mark_call_success(call_id=call_id, reason="Checked product catalog and stock", db_path=temp_db)
    assert updated is True

    # Step 3: Finalize call on session end
    final_rec = finalize_call(call_id=call_id, db_path=temp_db)
    assert final_rec["status"] == "SUCCESS"
    assert final_rec["end_time"] is not None

    # Step 4: Verify stats
    stats = get_call_stats(db_path=temp_db)
    assert stats["total_calls"] == 1
    assert stats["successful_calls"] == 1
    assert stats["failed_calls"] == 0
    assert stats["success_rate"] == "100.0%"


def test_call_lifecycle_failure(temp_db):
    """Test recording a call where caller disconnects before completing an enquiry (FAILED condition)."""
    call_id = "room-test-102"
    user_id = "caller-bob"

    # Start call
    record_call_start(call_id=call_id, user_id=user_id, db_path=temp_db)

    # Disconnect without marking success
    final_rec = finalize_call(call_id=call_id, db_path=temp_db)
    assert final_rec["status"] == "FAILED"

    # Verify stats
    stats = get_call_stats(db_path=temp_db)
    assert stats["total_calls"] == 1
    assert stats["successful_calls"] == 0
    assert stats["failed_calls"] == 1
    assert stats["success_rate"] == "0.0%"


def test_aggregated_stats(temp_db):
    """Test multiple calls (2 successful, 1 failed) stats output."""
    record_call_start("call-1", "user-1", temp_db)
    mark_call_success("call-1", "Product enquiry", temp_db)
    finalize_call("call-1", temp_db)

    record_call_start("call-2", "user-2", temp_db)
    mark_call_success("call-2", "Order total checked", temp_db)
    finalize_call("call-2", temp_db)

    record_call_start("call-3", "user-3", temp_db)
    finalize_call("call-3", temp_db)

    stats = get_call_stats(temp_db)
    assert stats["total_calls"] == 3
    assert stats["successful_calls"] == 2
    assert stats["failed_calls"] == 1
    assert stats["success_rate"] == "66.7%"
