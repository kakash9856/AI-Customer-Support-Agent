

import sqlite3
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).parent / "tickets.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_users_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT DEFAULT 'customer'
        )
    """)

    # Existing database mein role column add karega
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]

    if "role" not in columns:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN role TEXT DEFAULT 'customer'
        """)

    conn.commit()
    conn.close()


def hash_password(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()


def register_user(name, email, password):
    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO users (
                name, email, password_hash, salt, role
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name,
            email.lower(),
            password_hash,
            salt,
            "customer"
        ))

        conn.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError:
        return False, "This email is already registered."

    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, password_hash, salt, role
        FROM users
        WHERE email = ?
    """, (email.lower(),))

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    user_id, name, email, stored_hash, salt, role = user

    entered_hash = hash_password(password, salt)

    if secrets.compare_digest(entered_hash, stored_hash):
        return {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role
        }

    return None
def update_user_role(email, role):
    allowed_roles = ["customer", "admin"]

    if role not in allowed_roles:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET role = ?
        WHERE email = ?
    """, (role, email.lower()))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    return updated > 0


create_users_table()
