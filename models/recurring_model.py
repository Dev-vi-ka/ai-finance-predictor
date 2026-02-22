import sqlite3
from config import DATABASE_PATH


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# Get active recurring expenses
def get_recurring_expenses_by_user(user_id):
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT * FROM recurring_expenses
        WHERE user_id = ? AND active = 1
        ORDER BY billing_day
    """, (user_id,)).fetchall()

    conn.close()
    return rows


# Add recurring expense
def add_recurring_expense(user_id, title, amount, category, billing_day):
    conn = get_db_connection()

    conn.execute("""
        INSERT INTO recurring_expenses
        (user_id, title, amount, category, billing_day)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, title, amount, category, billing_day))

    conn.commit()
    conn.close()


# Soft delete (Deactivate instead of delete)
def deactivate_recurring_expense(expense_id, user_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE recurring_expenses
        SET active = 0
        WHERE id = ? AND user_id = ?
    """, (expense_id, user_id))

    conn.commit()
    conn.close()
