from flask import Blueprint, render_template, session, redirect, url_for
from models.transaction_model import (
    get_transactions_by_user,
    get_financial_summary,
    get_expense_by_category
)

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

    # -------- Fetch Data --------
    transactions = get_transactions_by_user(user_id)

    # Latest 5 transactions
    recent_transactions = transactions[:5]

    # Summary calculations (from DB function)
    total_income, total_expense, savings = get_financial_summary(user_id)

    # Category-wise expenses
    category_data = get_expense_by_category(user_id)

    # Placeholder Financial Health Score
    # (Later we replace this with rule-based logic or ML)
    health_score = 80

    return render_template(
        'index.html',
        user_name=session.get('user_name', 'User'),
        recent_transactions=recent_transactions,
        total_income=total_income,
        total_expense=total_expense,
        savings=savings,
        health_score=health_score,
        category_data=category_data
    )
