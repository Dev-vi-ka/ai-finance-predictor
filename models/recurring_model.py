import sqlite3
from config import DATABASE_PATH
from datetime import datetime


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


# Process recurring expenses - auto-create transactions on billing day
def process_recurring_expenses():
    """Automatically create transactions for recurring expenses on their billing day."""
    from models.transaction_model import add_transaction
    
    conn = get_db_connection()
    today = datetime.now().day
    
    # Get all active recurring expenses for today's billing day
    recurring = conn.execute("""
        SELECT * FROM recurring_expenses
        WHERE active = 1 AND billing_day = ?
    """, (today,)).fetchall()
    
    created_count = 0
    
    for expense in recurring:
        user_id = expense['user_id']
        
        # Check if transaction already exists for today
        existing = conn.execute("""
            SELECT id FROM transactions
            WHERE user_id = ? AND date = ? AND amount = ? AND category = ?
        """, (user_id, datetime.now().strftime('%Y-%m-%d'), -expense['amount'], expense['category'])).fetchone()
        
        if not existing:
            try:
                add_transaction(
                    user_id=user_id,
                    amount=-expense['amount'],  # Store as negative
                    description=f"Recurring: {expense['title']}",
                    category=expense['category'],
                    date=datetime.now().strftime('%Y-%m-%d'),
                    is_auto_tagged=1
                )
                created_count += 1
            except Exception as e:
                print(f"Error processing recurring expense {expense['id']}: {e}")
    
    conn.close()
    
    if created_count > 0:
        print(f"✓ Processed {created_count} recurring expenses.")

