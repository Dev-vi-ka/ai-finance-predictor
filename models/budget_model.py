import sqlite3
from config import DATABASE_PATH
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------- Set Budget Limit --------
def set_budget(user_id, category, limit_amount, month=None):
    """Set or update budget limit for a category.
    
    Args:
        user_id: User ID
        category: Expense category (e.g., 'Food', 'Transport')
        limit_amount: Monthly limit for this category
        month: Month in YYYY-MM format (default: current month)
    """
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if budget exists
    existing = cursor.execute(
        "SELECT id FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
        (user_id, category, month)
    ).fetchone()
    
    if existing:
        cursor.execute(
            "UPDATE budgets SET limit_amount = ? WHERE user_id = ? AND category = ? AND month = ?",
            (limit_amount, user_id, category, month)
        )
    else:
        cursor.execute("""
            INSERT INTO budgets (user_id, category, limit_amount, month)
            VALUES (?, ?, ?, ?)
        """, (user_id, category, limit_amount, month))
    
    conn.commit()
    conn.close()


# -------- Get Budget --------
def get_budget(user_id, category, month=None):
    """Get budget limit for a category."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    conn = get_db_connection()
    budget = conn.execute(
        "SELECT * FROM budgets WHERE user_id = ? AND category = ? AND month = ?",
        (user_id, category, month)
    ).fetchone()
    conn.close()
    return budget


# -------- Get All Budgets for User --------
def get_all_budgets(user_id, month=None):
    """Get all budgets for a user in a specific month."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    conn = get_db_connection()
    budgets = conn.execute(
        "SELECT * FROM budgets WHERE user_id = ? AND month = ?",
        (user_id, month)
    ).fetchall()
    conn.close()
    return budgets


# -------- Calculate Category Spending --------
def get_category_spending(user_id, category, month=None):
    """Calculate total spending for a category in a month."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    conn = get_db_connection()
    result = conn.execute("""
        SELECT COALESCE(SUM(ABS(amount)), 0) as total
        FROM transactions
        WHERE user_id = ? AND category = ? AND date LIKE ? AND amount < 0
    """, (user_id, category, f"{month}%")).fetchone()
    conn.close()
    
    return float(result['total']) if result else 0


# -------- Calculate Budget Usage Percentage --------
def get_budget_usage_percentage(user_id, category, month=None):
    """Calculate percentage of budget used for a category."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    budget = get_budget(user_id, category, month)
    if not budget or budget['limit_amount'] == 0:
        return 0
    
    spending = get_category_spending(user_id, category, month)
    percentage = (spending / budget['limit_amount']) * 100
    
    return round(percentage, 2)


# -------- Get Budget Status --------
def get_budget_status(user_id, category, month=None):
    """Get budget status including spending, limit, and percentage."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    budget = get_budget(user_id, category, month)
    
    if not budget:
        return None
    
    spending = get_category_spending(user_id, category, month)
    percentage = get_budget_usage_percentage(user_id, category, month)
    
    return {
        'category': category,
        'limit': budget['limit_amount'],
        'spent': spending,
        'remaining': budget['limit_amount'] - spending,
        'percentage': percentage,
        'month': month,
        'status': 'Critical' if percentage >= 100 else 'Warning' if percentage >= 80 else 'OK'
    }


# -------- Get All Budget Status for User --------
def get_all_budget_status(user_id, month=None):
    """Get budget status for all categories."""
    if month is None:
        month = date.today().strftime("%Y-%m")
    
    budgets = get_all_budgets(user_id, month)
    status_list = []
    
    for budget in budgets:
        status = get_budget_status(user_id, budget['category'], month)
        if status:
            status_list.append(status)
    
    return status_list


# -------- Get Last Month Comparison --------
def get_last_month_spending(user_id, category):
    """Get spending from last month for comparison."""
    current_date = date.today()
    last_month = current_date - relativedelta(months=1)
    last_month_str = last_month.strftime("%Y-%m")
    
    return get_category_spending(user_id, category, last_month_str)


# -------- Check if Budget Threshold Crossed --------
def check_budget_threshold(user_id, category, threshold_percentage=80):
    """Check if spending exceeds threshold percentage."""
    percentage = get_budget_usage_percentage(user_id, category)
    return percentage >= threshold_percentage


# -------- Delete Budget --------
def delete_budget(user_id, budget_id):
    """Delete a budget."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM budgets WHERE id = ? AND user_id = ?",
        (budget_id, user_id)
    )
    conn.commit()
    conn.close()
