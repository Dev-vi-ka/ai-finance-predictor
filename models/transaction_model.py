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


# ---------------- Financial Health Score ----------------
def calculate_health_score(user_id):
    """Calculate financial health score (0-100) based on spending patterns.
    
    Factors:
    - Savings ratio (30%): Higher is better
    - Expense ratio (30%): Lower is better
    - Consistency (20%): Less volatility is better
    - Frequency (20%): Regular activity is healthy
    """
    income, expenses, savings = get_financial_summary(user_id)
    
    score = 50  # Base score
    
    # Factor 1: Savings Ratio (0-30 points)
    if income == 0:
        savings_ratio_points = 0
    else:
        savings_ratio = (savings / income) * 100
        if savings_ratio >= 30:
            savings_ratio_points = 30
        elif savings_ratio >= 20:
            savings_ratio_points = 25
        elif savings_ratio >= 10:
            savings_ratio_points = 20
        elif savings_ratio >= 0:
            savings_ratio_points = 10
        else:
            savings_ratio_points = 0
    
    score += savings_ratio_points
    
    # Factor 2: Expense Ratio (0-30 points)
    if income == 0:
        expense_ratio_points = 0
    else:
        expense_ratio = (expenses / income) * 100
        if expense_ratio <= 50:
            expense_ratio_points = 30
        elif expense_ratio <= 60:
            expense_ratio_points = 25
        elif expense_ratio <= 70:
            expense_ratio_points = 20
        elif expense_ratio <= 80:
            expense_ratio_points = 10
        else:
            expense_ratio_points = 0
    
    score += expense_ratio_points
    
    # Factor 3: Spending Consistency (0-20 points)
    conn = get_db_connection()
    monthly = conn.execute("""
        SELECT SUM(ABS(amount)) as total
        FROM transactions
        WHERE user_id = ? AND amount < 0
        GROUP BY strftime('%Y-%m', date)
        ORDER BY date DESC
        LIMIT 3
    """, (user_id,)).fetchall()
    conn.close()
    
    if len(monthly) >= 2:
        amounts = [row['total'] for row in monthly]
        avg = sum(amounts) / len(amounts)
        
        # Calculate coefficient of variation
        if avg > 0:
            variance = sum((x - avg) ** 2 for x in amounts) / len(amounts)
            std_dev = variance ** 0.5
            cv = (std_dev / avg)  # Coefficient of variation
            
            if cv <= 0.1:
                consistency_points = 20
            elif cv <= 0.2:
                consistency_points = 15
            elif cv <= 0.3:
                consistency_points = 10
            else:
                consistency_points = 5
        else:
            consistency_points = 0
    else:
        consistency_points = 0
    
    score += consistency_points
    
    # Ensure score is within 0-100
    return max(0, min(100, int(score)))
