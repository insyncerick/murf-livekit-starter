import json
import os
import sqlite3
import random
from datetime import datetime, timezone

# SQLite database location for escalations
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "escalations.db"
)


def _ensure_data_directory():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_escalation_db():
    """Create the SQLite database and escalations table if they don't exist."""
    _ensure_data_directory()

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS escalations (
            id TEXT PRIMARY KEY,
            user_id TEXT,
            name TEXT,
            reason TEXT,
            summary TEXT,
            agent_checked TEXT,
            urgency TEXT,
            language TEXT,
            preferred_contact TEXT,
            status TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()

    print(f"[ESCALATION DB] Ready: {DB_PATH}")


def generate_reference_id() -> str:
    """Generate a unique reference ID like ESC-84920."""
    return f"ESC-{random.randint(10000, 99999)}"


def save_escalation(
    user_id: str,
    name: str,
    reason: str,
    summary: str,
    agent_checked: str,
    urgency: str = "medium",
    language: str = "English",
    preferred_contact: str = "phone call",
) -> dict:
    """
    Save a human escalation request to SQLite database.
    Returns the created record including generated reference ID.
    """
    _ensure_data_directory()
    init_escalation_db()

    reference_id = generate_reference_id()
    created_at = datetime.now(timezone.utc).isoformat()
    status = "OPEN"

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        INSERT INTO escalations (
            id,
            user_id,
            name,
            reason,
            summary,
            agent_checked,
            urgency,
            language,
            preferred_contact,
            status,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reference_id,
        user_id or "UNKNOWN",
        name or "Valued Customer",
        reason,
        summary,
        agent_checked,
        urgency,
        language,
        preferred_contact,
        status,
        created_at,
    ))

    conn.commit()
    conn.close()

    print(f"[ESCALATION DB] Created escalation {reference_id} for user {user_id}")

    return {
        "reference_id": reference_id,
        "user_id": user_id,
        "name": name,
        "reason": reason,
        "summary": summary,
        "agent_checked": agent_checked,
        "urgency": urgency,
        "language": language,
        "preferred_contact": preferred_contact,
        "status": status,
        "created_at": created_at,
    }


def get_open_escalations() -> list[dict]:
    """Retrieve all open human escalation requests."""
    _ensure_data_directory()
    init_escalation_db()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT
            id,
            user_id,
            name,
            reason,
            summary,
            agent_checked,
            urgency,
            language,
            preferred_contact,
            status,
            created_at
        FROM escalations
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    escalations = []
    for row in rows:
        escalations.append({
            "id": row[0],
            "user_id": row[1],
            "name": row[2],
            "reason": row[3],
            "summary": row[4],
            "agent_checked": row[5],
            "urgency": row[6],
            "language": row[7],
            "preferred_contact": row[8],
            "status": row[9],
            "created_at": row[10],
        })

    return escalations
