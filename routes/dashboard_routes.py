from flask import Blueprint, render_template, session, redirect, url_for, request
from config import ADMIN_EMAILS
from models.transaction_model import (
    get_transactions_by_user,
    get_financial_summary,
    get_expense_by_category,
    calculate_health_score,
    get_expense_by_month_and_category,
    get_monthly_summary,
    get_all_available_months
)
from models.user_model import get_user_by_id
from models.budget_model import get_all_budget_status
from models.alert_model import get_unread_alerts, get_unread_alert_count

dashboard_bp = Blueprint(
    'dashboard',
    __name__,
    template_folder='../templates/dashboard'
)

@dashboard_bp.route('/dashboard')
def index():

    # -------- Authentication Check --------
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    
    # Get selected month from query params (optional)
    selected_month = request.args.get('month', None)

    # -------- Fetch Data --------
    transactions = get_transactions_by_user(user_id)

    # Latest 5 transactions
    recent_transactions = transactions[:5]

    # Summary calculations (from DB function)
    total_income, total_expense, savings = get_financial_summary(user_id)

    # Category-wise expenses (all time or monthly)
    if selected_month:
        category_data = get_expense_by_month_and_category(user_id, selected_month)
        # Convert to same format as get_expense_by_category
        category_data = [{"category": c["category"], "total": c["total"]} for c in category_data]
        monthly_summary = get_monthly_summary(user_id, selected_month)
    else:
        category_data = get_expense_by_category(user_id)
        monthly_summary = None

    # Calculate Financial Health Score
    health_score = calculate_health_score(user_id)

    # --- Fetch Budget Data ---
    budgets = get_all_budget_status(user_id)
    unread_alerts = get_unread_alerts(user_id)
    alert_count = get_unread_alert_count(user_id)
    
    # Get critical and warning budgets
    critical_budgets = [b for b in budgets if b['status'] == 'Critical']
    warning_budgets = [b for b in budgets if b['status'] == 'Warning']
    
    # Get all available months for the filter dropdown
    available_months = get_all_available_months(user_id)
    
    # Check if current user is admin
    user = get_user_by_id(user_id)
    is_admin = user and user['email'] in ADMIN_EMAILS

    return render_template(
        'index.html',
        user_name=session.get('user_name', 'User'),
        recent_transactions=recent_transactions,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        health_score=health_score,
        category_data=category_data,
        budgets=budgets,
        critical_budgets=critical_budgets,
        warning_budgets=warning_budgets,
        unread_alerts=unread_alerts,
        alert_count=alert_count,
        selected_month=selected_month,
        monthly_summary=monthly_summary,
        available_months=available_months,
        is_admin=is_admin
    )
