import sqlite3
from config import DATABASE_PATH

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_user(name, email, password_hash):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        (name, email, password_hash)
    )
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()
    conn.close()
    return user
