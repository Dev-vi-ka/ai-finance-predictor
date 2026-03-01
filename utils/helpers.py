"""Common helper functions for the application."""

from datetime import datetime, timedelta
from functools import wraps
from flask import session, redirect, url_for, jsonify
import re


def login_required(f):
    """Decorator to check if user is logged in."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def api_login_required(f):
    """Decorator to check authentication for API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_amount(amount):
    """Validate transaction amount."""
    try:
        val = float(amount)
        return val > 0
    except (ValueError, TypeError):
        return False


def validate_date(date_str, format_str='%Y-%m-%d'):
    """Validate date format."""
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def format_currency(amount, symbol="₹"):
    """Format amount as currency string."""
    return f"{symbol} {abs(amount):,.2f}"


def get_month_range(offset=0):
    """Get start and end dates for a month.
    
    Args:
        offset: 0 for current month, -1 for last month, etc.
    
    Returns:
        Tuple of (start_date, end_date) as strings 'YYYY-MM-DD'
    """
    today = datetime.now()
    
    # Calculate target month
    if offset == 0:
        target_month = today
    else:
        weeks = abs(offset) * 4  # Approximate
        target_month = today + timedelta(weeks=weeks)
    
    # Get first day of month
    start_date = target_month.replace(day=1)
    
    # Get last day of month
    if start_date.month == 12:
        end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
    
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')


def calculate_days_until_billing_day(billing_day):
    """Calculate days until next billing date."""
    today = datetime.now()
    current_day = today.day
    
    if billing_day >= current_day:
        days_until = billing_day - current_day
    else:
        # Next month
        if today.month == 12:
            next_month_first = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month_first = today.replace(month=today.month + 1, day=1)
        
        billing_date = next_month_first.replace(day=min(billing_day, 28))
        days_until = (billing_date - today.date()).days
    
    return max(0, days_until)


def get_spending_trend(expenses_list):
    """Determine if spending is increasing, stable, or decreasing.
    
    Args:
        expenses_list: List of expense amounts
        
    Returns:
        String: "increasing", "stable", or "decreasing"
    """
    if len(expenses_list) < 2:
        return "stable"
    
    # Compare average of first half vs second half
    mid = len(expenses_list) // 2
    first_half_avg = sum(expenses_list[:mid]) / len(expenses_list[:mid])
    second_half_avg = sum(expenses_list[mid:]) / len(expenses_list[mid:])
    
    difference = ((second_half_avg - first_half_avg) / first_half_avg) * 100
    
    if difference > 5:
        return "increasing"
    elif difference < -5:
        return "decreasing"
    else:
        return "stable"


def generate_insights(income, expenses, savings):
    """Generate spending insights based on financial data.
    
    Args:
        income: Total income
        expenses: Total expenses
        savings: Income - expenses
        
    Returns:
        List of insight strings
    """
    insights = []
    
    if income == 0:
        insights.append("Start recording income to get insights.")
        return insights
    
    expense_ratio = (expenses / income) * 100
    savings_ratio = (savings / income) * 100
    
    if expense_ratio > 80:
        insights.append("⚠️ Expenses are very high - consider budgeting.")
    elif expense_ratio > 60:
        insights.append("📊 Expenses are moderate - monitor spending.")
    else:
        insights.append("✅ Good expense ratio - keep it up!")
    
    if savings_ratio > 30:
        insights.append("💰 Great savings rate - excellent financial health!")
    elif savings_ratio > 10:
        insights.append("📈 Reasonable savings - continue this trend.")
    elif savings_ratio > 0:
        insights.append("⚠️ Low savings - try to increase savings rate.")
    else:
        insights.append("🔴 Negative savings - spending exceeds income!")
    
    return insights
