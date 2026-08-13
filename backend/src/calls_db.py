import os
import sqlite3
from datetime import datetime, timezone
from typing import Dict, Any

# SQLite database location for call outcome tracking
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "calls.db"
)


def _ensure_data_directory():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_calls_db(db_path: str = DB_PATH):
    """Create the SQLite database and calls table if they don't exist."""
    _ensure_data_directory()

    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS calls (
            call_id TEXT PRIMARY KEY,
            user_id TEXT,
            status TEXT NOT NULL,
            reason TEXT,
            start_time TEXT NOT NULL,
            end_time TEXT,
            duration_seconds INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def record_call_start(call_id: str, user_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Record the start of a new call session. Initial status is FAILED until
    a success condition (product enquiry/lookup) is fulfilled.
    """
    _ensure_data_directory()
    init_calls_db(db_path)

    start_time = datetime.now(timezone.utc).isoformat()
    conn = sqlite3.connect(db_path)
    conn.execute("""
        INSERT OR REPLACE INTO calls (
            call_id, user_id, status, reason, start_time, end_time, duration_seconds
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        call_id,
        user_id or "UNKNOWN",
        "FAILED",
        "Call initiated; awaiting enquiry completion",
        start_time,
        None,
        0
    ))
    conn.commit()
    conn.close()

    return {
        "call_id": call_id,
        "user_id": user_id,
        "status": "FAILED",
        "start_time": start_time
    }


def mark_call_success(call_id: str, reason: str = "Enquiry completed successfully", db_path: str = DB_PATH) -> bool:
    """
    Mark an active call as SUCCESSFUL (e.g. caller found product / completed enquiry).
    """
    _ensure_data_directory()
    init_calls_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        UPDATE calls 
        SET status = 'SUCCESS', reason = ?
        WHERE call_id = ?
    """, (reason, call_id))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def finalize_call(call_id: str, db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Finalize a call session when the room closes or participant disconnects.
    Calculates duration and sets end_time.
    """
    _ensure_data_directory()
    init_calls_db(db_path)

    end_time_dt = datetime.now(timezone.utc)
    end_time_str = end_time_dt.isoformat()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT start_time, status FROM calls WHERE call_id = ?", (call_id,))
    row = cursor.fetchone()

    duration = 0
    if row and row["start_time"]:
        try:
            start_dt = datetime.fromisoformat(row["start_time"])
            duration = int((end_time_dt - start_dt).total_seconds())
        except Exception:
            duration = 0

    conn.execute("""
        UPDATE calls 
        SET end_time = ?, duration_seconds = ?
        WHERE call_id = ?
    """, (end_time_str, duration, call_id))
    conn.commit()

    cursor = conn.execute("SELECT * FROM calls WHERE call_id = ?", (call_id,))
    updated_row = cursor.fetchone()
    conn.close()

    if updated_row:
        return dict(updated_row)
    return {}


def get_call_stats(db_path: str = DB_PATH) -> Dict[str, Any]:
    """
    Get aggregated counts for Total Calls, Successful Calls, and Failed Calls.
    Strictly protects caller PII — returns only summary counts.
    """
    _ensure_data_directory()
    init_calls_db(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.execute("""
        SELECT 
            COUNT(*) as total_calls,
            SUM(CASE WHEN status = 'SUCCESS' THEN 1 ELSE 0 END) as successful_calls,
            SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_calls
        FROM calls
    """)
    row = cursor.fetchone()
    conn.close()

    total = row[0] or 0
    successful = row[1] or 0
    failed = row[2] or 0

    return {
        "total_calls": total,
        "successful_calls": successful,
        "failed_calls": failed,
        "success_rate": f"{round((successful / total * 100), 1)}%" if total > 0 else "0.0%"
    }
