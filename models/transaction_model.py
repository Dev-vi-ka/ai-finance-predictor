import sqlite3
from config import DATABASE_PATH


def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- Add Transaction ----------------
def add_transaction(user_id, amount, description, category, date, is_auto_tagged=0):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO transactions 
        (user_id, amount, description, category, date, is_auto_tagged)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, amount, description, category, date, is_auto_tagged))
    conn.commit()
    conn.close()


# ---------------- Get All Transactions ----------------
def get_transactions_by_user(user_id):
    conn = get_db_connection()
    rows = conn.execute("""
        SELECT * FROM transactions
        WHERE user_id = ?
        ORDER BY date DESC
    """, (user_id,)).fetchall()
    conn.close()
    return rows


# ---------------- Delete Transaction ----------------
def delete_transaction(transaction_id, user_id):
    conn = get_db_connection()
    conn.execute("""
        DELETE FROM transactions
        WHERE id = ? AND user_id = ?
    """, (transaction_id, user_id))
    conn.commit()
    conn.close()


# ---------------- Financial Summary ----------------
def get_financial_summary(user_id):
    conn = get_db_connection()

    income = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = ? AND amount > 0
    """, (user_id,)).fetchone()[0]

    expense = conn.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = ? AND amount < 0
    """, (user_id,)).fetchone()[0]

    conn.close()

    total_expense = abs(expense)
    savings = income - total_expense

    return income, total_expense, savings


# ---------------- Expense by Category ----------------
def get_expense_by_category(user_id):
    conn = get_db_connection()

    rows = conn.execute("""
        SELECT category, ABS(SUM(amount)) as total
        FROM transactions
        WHERE user_id = ? AND amount < 0
        GROUP BY category
    """, (user_id,)).fetchall()

    conn.close()

    return [
        {"category": row["category"], "total": row["total"]}
        for row in rows
    ]


# ---------------- Monthly Expenses for ML ----------------
def get_monthly_expenses(user_id):
    conn = get_db_connection()
    
    # SQLite strftime('%Y-%m', date) returns 'YYYY-MM'
    rows = conn.execute("""
        SELECT strftime('%Y-%m', date) as month, SUM(ABS(amount)) as total
        FROM transactions
        WHERE user_id = ? AND amount < 0
        GROUP BY month
        ORDER BY month ASC
    """, (user_id,)).fetchall()
    
    conn.close()
    
    return [{"month": row["month"], "total": row["total"]} for row in rows]
