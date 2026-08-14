import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger("returns_db")

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
DB_PATH = os.path.join(DB_DIR, "returns.db")

def init_returns_db() -> None:
    os.makedirs(DB_DIR, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                user_id TEXT,
                customer_name TEXT,
                order_date TEXT,
                items TEXT,
                total_amount REAL,
                status TEXT,
                delivery_date TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS return_requests (
                return_id TEXT PRIMARY KEY,
                order_id TEXT,
                user_id TEXT,
                customer_name TEXT,
                items TEXT,
                reason TEXT,
                refund_amount REAL,
                status TEXT,
                created_at TEXT
            )
            """
        )
        conn.commit()

        # Seed sample mock orders if empty
        cursor.execute("SELECT COUNT(*) FROM orders")
        if cursor.fetchone()[0] == 0:
            sample_orders = [
                ("ORD-1001", "tilak", "Tilak", "2026-08-10", "1x Fortune Sunflower Oil (1L), 2x Amul Taaza Milk (500ml), 1x Daawat Basmati Rice (5kg)", 710.0, "Delivered", "2026-08-11"),
                ("ORD-1002", "tilak", "Tilak", "2026-08-12", "3x Aashirvaad Atta (5kg), 1x Tata Salt (1kg)", 625.0, "Delivered", "2026-08-13"),
                ("ORD-1003", "guest", "Customer", "2026-08-08", "2x Tata Tea Gold (500g), 1x Sugar (1kg)", 380.0, "Delivered", "2026-08-09"),
            ]
            cursor.executemany(
                "INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                sample_orders,
            )
            conn.commit()
            logger.info("Seeded initial return orders in returns.db")

def get_order(order_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT order_id, user_id, customer_name, order_date, items, total_amount, status, delivery_date FROM orders WHERE UPPER(order_id) = UPPER(?)", (order_id.strip(),))
        row = cursor.fetchone()
        if row:
            return {
                "order_id": row[0],
                "user_id": row[1],
                "customer_name": row[2],
                "order_date": row[3],
                "items": row[4],
                "total_amount": row[5],
                "status": row[6],
                "delivery_date": row[7],
            }
    return None

def get_latest_order_for_user(user_id: str) -> dict | None:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT order_id, user_id, customer_name, order_date, items, total_amount, status, delivery_date FROM orders WHERE user_id = ? ORDER BY order_date DESC LIMIT 1",
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            return {
                "order_id": row[0],
                "user_id": row[1],
                "customer_name": row[2],
                "order_date": row[3],
                "items": row[4],
                "total_amount": row[5],
                "status": row[6],
                "delivery_date": row[7],
            }
    return None

def create_return_ticket(order_id: str, user_id: str, customer_name: str, items: str, reason: str, refund_amount: float) -> dict:
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    return_id = f"RET-{datetime.utcnow().strftime('%M%S')}"
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO return_requests (return_id, order_id, user_id, customer_name, items, reason, refund_amount, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (return_id, order_id, user_id, customer_name, items, reason, refund_amount, "Approved / Processing", now_str),
        )
        conn.commit()

    return {
        "return_id": return_id,
        "order_id": order_id,
        "items": items,
        "refund_amount": refund_amount,
        "status": "Approved / Processing",
        "message": f"Refund of ₹{refund_amount:.2f} initiated. It will reflect in your account within 2-4 business hours.",
    }
