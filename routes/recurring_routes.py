from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.recurring_model import (
    get_recurring_expenses_by_user,
    add_recurring_expense,
    deactivate_recurring_expense
)
from utils.auth_utils import validate_amount

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
        try:
            title = request.form.get('title', '').strip()
            amount = float(request.form.get('amount', 0))
            category = request.form.get('category', '').strip()
            billing_day = int(request.form.get('billing_day', 1))
            
            # Validate inputs
            if not title or len(title) < 2:
                flash("Title must be at least 2 characters.", "danger")
                return redirect(url_for('recurring.add'))
            
            valid, msg = validate_amount(amount)
            if not valid:
                flash(msg, "danger")
                return redirect(url_for('recurring.add'))
            
            if not category or len(category) < 2:
                flash("Category must be at least 2 characters.", "danger")
                return redirect(url_for('recurring.add'))
            
            if billing_day < 1 or billing_day > 31:
                flash("Billing day must be between 1 and 31.", "danger")
                return redirect(url_for('recurring.add'))
            
            add_recurring_expense(
                session['user_id'],
                title,
                amount,
                category,
                billing_day
            )

            flash("Recurring expense added successfully", "success")
            return redirect(url_for('recurring.index'))
        
        except ValueError:
            flash("Invalid input data", "danger")
            return redirect(url_for('recurring.add'))
        except Exception as e:
            flash(f"Error adding recurring expense: {str(e)}", "danger")
            return redirect(url_for('recurring.add'))

    return render_template('recurring/add.html')


# Deactivate recurring expense
@recurring_bp.route('/recurring/delete/<int:expense_id>')
def delete(expense_id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        deactivate_recurring_expense(expense_id, session['user_id'])
        flash("Recurring expense removed", "warning")
    except Exception as e:
        flash(f"Error removing recurring expense: {str(e)}", "danger")
    
    return redirect(url_for('recurring.index'))
