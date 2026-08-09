import json
import os
import sqlite3
from datetime import datetime, timezone


# SQLite database location
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "data",
    "users.db"
)


def _ensure_data_directory():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


def init_db():
    """Create the SQLite database and users table if they don't exist."""
    _ensure_data_directory()

    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            language_preference TEXT,
            facts TEXT,
            last_interaction TEXT
        )
    """)

    conn.commit()
    conn.close()

    print(f"[DATABASE] Ready: {DB_PATH}")


def get_user(user_id: str) -> dict:
    """Find a user by their stable user_id."""

    if not user_id:
        return {}

    _ensure_data_directory()

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.execute("""
        SELECT
            user_id,
            name,
            language_preference,
            facts,
            last_interaction
        FROM users
        WHERE user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return {}

    saved_user_id, name, language_preference, facts, last_interaction = row

    try:
        facts_dict = json.loads(facts) if facts else {}
    except json.JSONDecodeError:
        facts_dict = {}

    return {
        "user_id": saved_user_id,
        "name": name,
        "language_preference": language_preference,
        "facts": facts_dict,
        "last_interaction": last_interaction,
    }


def save_user(
    user_id: str,
    name: str,
    language_preference: str = "",
    facts: dict | None = None,
) -> bool:
    """Create or update a user's memory."""

    if not user_id:
        print("[DATABASE] ERROR: user_id is empty")
        return False

    _ensure_data_directory()

    if facts is None:
        facts = {}

    last_interaction = datetime.now(timezone.utc).isoformat()

    try:
        conn = sqlite3.connect(DB_PATH)

        conn.execute("""
            INSERT INTO users (
                user_id,
                name,
                language_preference,
                facts,
                last_interaction
            )
            VALUES (?, ?, ?, ?, ?)

            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                language_preference = excluded.language_preference,
                facts = excluded.facts,
                last_interaction = excluded.last_interaction
        """, (
            user_id,
            name,
            language_preference,
            json.dumps(facts),
            last_interaction,
        ))

        conn.commit()
        conn.close()

        # IMPORTANT:
        # Agent needs this True to know that saving succeeded.
        print(
            f"[DATABASE] SAVED: "
            f"user_id={user_id}, name={name}"
        )

        return True

    except Exception as e:
        print(f"[DATABASE] SAVE ERROR: {e}")
        return False
