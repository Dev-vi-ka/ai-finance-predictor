from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.recurring_model import (
    get_recurring_expenses_by_user,
    add_recurring_expense,
    deactivate_recurring_expense
)

recurring_bp = Blueprint('recurring', __name__, template_folder='../templates/recurring')


# View recurring expenses
@recurring_bp.route('/recurring')
def index():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    expenses = get_recurring_expenses_by_user(session['user_id'])

    return render_template('recurring/index.html', expenses=expenses)


# Add recurring expense
@recurring_bp.route('/recurring/add', methods=['GET', 'POST'])
def add():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':

        title = request.form['title']
        amount = float(request.form['amount'])
        category = request.form['category']
        billing_day = int(request.form['billing_day'])

        add_recurring_expense(
            session['user_id'],
            title,
            amount,
            category,
            billing_day
        )

        flash("Recurring expense added successfully", "success")
        return redirect(url_for('recurring.index'))

    return render_template('recurring/add.html')


# Deactivate recurring expense
@recurring_bp.route('/recurring/delete/<int:expense_id>')
def delete(expense_id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    deactivate_recurring_expense(expense_id, session['user_id'])

    flash("Recurring expense removed", "warning")
    return redirect(url_for('recurring.index'))
