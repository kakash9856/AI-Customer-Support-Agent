

import sqlite3
import hashlib
import secrets
from pathlib import Path

DB_PATH = Path(__file__).parent / "tickets.db"


# DEBUG: Database information
def debug_database_info():
    return {
        "database_path": str(DB_PATH.resolve()),
        "database_exists": DB_PATH.exists(),
        "database_size": DB_PATH.stat().st_size if DB_PATH.exists() else 0
    }


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


# DEBUG: Total registered users
def debug_user_count():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return count
    finally:
        conn.close()


def register_user(name, email, password):
    email = email.strip().lower()

    salt = secrets.token_hex(16)
    password_hash = hash_password(password, salt)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT id, email
            FROM users
            WHERE LOWER(TRIM(email)) = ?
        """, (email,))

        existing_user = cursor.fetchone()

        if existing_user:
            return False, (
                f"Email already exists. "
                f"Database path: {DB_PATH.resolve()} | "
                f"Matched email: {existing_user[1]}"
            )

        cursor.execute("""
            INSERT INTO users (
                name, email, password_hash, salt, role
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            name.strip(),
            email,
            password_hash,
            salt,
            "customer"
        ))

        conn.commit()
        return True, "Registration successful!"

    except sqlite3.IntegrityError as e:
        return False, f"SQLite Integrity Error: {str(e)}"

    except Exception as e:
        return False, f"Unexpected Error: {type(e).__name__}: {str(e)}"

    finally:
        conn.close()


def login_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, email, password_hash, salt, role
        FROM users
        WHERE email = ?
    """, (email.strip().lower(),))

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
    """, (role, email.strip().lower()))

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    return updated > 0


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM users
        WHERE email = ?
    """, (email.strip().lower(),))

    user = cursor.fetchone()
    conn.close()

    return user is not None


def update_user_password(email, new_password):
    if len(new_password) < 8:
        return False, "Password must be at least 8 characters."

    salt = secrets.token_hex(16)
    password_hash = hash_password(new_password, salt)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET password_hash = ?, salt = ?
        WHERE email = ?
    """, (
        password_hash,
        salt,
        email.strip().lower()
    ))

    updated = cursor.rowcount

    conn.commit()
    conn.close()

    if updated:
        return True, "Password updated successfully!"

    return False, "Account not found."


# Create users table when this file is imported
create_users_table()
