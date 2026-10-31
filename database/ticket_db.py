
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "tickets.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_name TEXT,
            customer_email TEXT,
            issue TEXT NOT NULL,
            status TEXT DEFAULT 'Open',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(tickets)")
    columns = [column[1] for column in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute("""
            ALTER TABLE tickets ADD COLUMN user_id INTEGER
        """)

    conn.commit()
    conn.close()


def require_role(user_id, required_role):
    """Verify the user's role directly from the database."""

    if user_id is None:
        raise PermissionError("Login required.")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE id = ?",
        (user_id,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result or result[0] != required_role:
        raise PermissionError("You are not authorized for this action.")


def create_ticket(issue, customer_name="Guest",
                  customer_email="", user_id=None):

    require_role(user_id, "customer")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name, email FROM users WHERE id = ?",
        (user_id,)
    )
    customer = cursor.fetchone()

    if not customer:
        conn.close()
        raise PermissionError("Customer account not found.")

    ticket_id = "TKT-" + uuid.uuid4().hex[:8].upper()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO tickets (
            ticket_id, customer_name, customer_email,
            issue, status, created_at, user_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        customer[0],
        customer[1],
        issue,
        "Open",
        created_at,
        user_id
    ))

    conn.commit()
    conn.close()

    return ticket_id


def get_all_tickets(admin_user_id):
    require_role(admin_user_id, "admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_id, customer_name, customer_email,
               issue, status, created_at, user_id
        FROM tickets
        ORDER BY id DESC
    """)

    tickets = cursor.fetchall()
    conn.close()

    return tickets


def get_customer_tickets(user_id, requester_user_id):
    if user_id != requester_user_id:
        raise PermissionError("You can only view your own tickets.")

    require_role(requester_user_id, "customer")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_id, customer_name, customer_email,
               issue, status, created_at
        FROM tickets
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    tickets = cursor.fetchall()
    conn.close()

    return tickets


def search_ticket(ticket_id, admin_user_id):
    require_role(admin_user_id, "admin")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ticket_id, customer_name, customer_email,
               issue, status, created_at
        FROM tickets
        WHERE ticket_id = ?
    """, (ticket_id,))

    ticket = cursor.fetchone()
    conn.close()

    return ticket


def update_ticket_status(ticket_id, status, admin_user_id):
    require_role(admin_user_id, "admin")

    allowed_statuses = ["Open", "In Progress", "Resolved"]

    if status not in allowed_statuses:
        raise ValueError("Invalid ticket status.")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tickets
        SET status = ?
        WHERE ticket_id = ?
    """, (status, ticket_id))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    return updated > 0


create_table()
