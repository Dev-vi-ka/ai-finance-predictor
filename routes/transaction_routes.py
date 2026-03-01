from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.transaction_model import add_transaction, get_transactions_by_user, delete_transaction
from ml.category_classifier import predict_category
from utils.auth_utils import validate_transaction_input, sanitize_string
from datetime import date

transaction_bp = Blueprint(
    'transaction',
    __name__,
    template_folder='../templates/transactions'
)


# -------- Add Transaction --------
@transaction_bp.route('/transactions/add', methods=['GET', 'POST'])
def add_transaction_route():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        user_id = session['user_id']

        try:
            amount = float(request.form['amount'])
            description = request.form['description']
            txn_type = request.form['type']   # income or expense
            txn_date = request.form['date']
        except (ValueError, KeyError):
            flash("Invalid input", "danger")
            return redirect(url_for('transaction.add_transaction_route'))
        
        # Validate input
        valid, errors = validate_transaction_input(description, amount, txn_type, txn_date)
        if not valid:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for('transaction.add_transaction_route'))
        
        # Sanitize description
        description = sanitize_string(description, 255)

        if txn_type == 'expense':
            category = predict_category(description)
            is_auto_tagged = 1
            amount = -abs(amount) # Store expenses as negative
        else:
            category = "Income"
            is_auto_tagged = 0
            amount = abs(amount) # Store income as positive

        try:
            add_transaction(
                user_id=user_id,
                amount=amount,
                description=description,
                category=category,
                date=txn_date,
                is_auto_tagged=is_auto_tagged
            )
            flash("Transaction added successfully", "success")
        except Exception as e:
            flash(f"Error adding transaction: {str(e)}", "danger")
            return redirect(url_for('transaction.add_transaction_route'))

        return redirect(url_for('transaction.history'))

    return render_template('add.html', today=date.today())


# -------- Transaction History --------
@transaction_bp.route('/transactions/history')
def history():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    transactions = get_transactions_by_user(session['user_id'])

    return render_template('history.html', transactions=transactions)


# -------- Delete Transaction --------
@transaction_bp.route('/transactions/delete/<int:txn_id>')
def delete(txn_id):

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        delete_transaction(txn_id, session['user_id'])
        flash("Transaction deleted", "info")
    except Exception as e:
        flash(f"Error deleting transaction: {str(e)}", "danger")
    
    return redirect(url_for('transaction.history'))
