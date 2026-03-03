from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file
from models.transaction_model import (
    add_transaction, get_transactions_by_user, delete_transaction,
    get_transactions_by_month, get_expense_by_month_and_category, get_monthly_summary
)
from models.budget_model import (
    get_budget, get_budget_usage_percentage, get_category_spending, check_budget_threshold
)
from models.alert_model import create_alert, alert_exists_today
from ml.category_classifier import predict_category
from utils.auth_utils import validate_transaction_input, sanitize_string
from datetime import date, datetime
import csv
import io
from werkzeug.utils import secure_filename

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
        
        # Check if this is a bulk upload or single transaction
        is_bulk_upload = request.form.get('bulk_upload') == 'true'
        
        if is_bulk_upload:
            # Handle bulk upload
            return handle_bulk_upload(user_id)
        else:
            # Handle single transaction
            return handle_single_transaction(user_id)

    return render_template('add.html', today=date.today())


def handle_single_transaction(user_id):
    """Handle adding a single transaction."""
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
        
        # --- Check Budget and Create Alert (for expenses only) ---
        if txn_type == 'expense':
            budget = get_budget(user_id, category)
            
            if budget:
                percentage = get_budget_usage_percentage(user_id, category)
                spent = get_category_spending(user_id, category)
                
                # Create alert if threshold crossed (only once per day)
                if percentage >= 100 and not alert_exists_today(user_id, 'budget_exceeded', category):
                    create_alert(
                        user_id=user_id,
                        alert_type='budget_exceeded',
                        category=category,
                        title=f'⚠️ {category} Budget Exceeded!',
                        message=f"You've exceeded your {category} budget! You've spent ${spent:.2f} of ${budget['limit_amount']:.2f}",
                        percentage=percentage
                    )
                    flash(f"⚠️ Budget Alert: You've used 100%+ of your {category} budget!", "warning")
                
                elif percentage >= 90 and not alert_exists_today(user_id, 'budget_critical', category):
                    create_alert(
                        user_id=user_id,
                        alert_type='budget_critical',
                        category=category,
                        title=f'🔴 {category} Budget Critical!',
                        message=f"You've used {percentage:.1f}% of your {category} budget. Spent: ${spent:.2f} of ${budget['limit_amount']:.2f}",
                        percentage=percentage
                    )
                    flash(f"🔴 Critical Alert: You've used {percentage:.1f}% of your {category} budget.", "warning")
                
                elif percentage >= 80 and not alert_exists_today(user_id, 'budget_warning', category):
                    create_alert(
                        user_id=user_id,
                        alert_type='budget_warning',
                        category=category,
                        title=f'📢 {category} Budget Warning',
                        message=f"You've used {percentage:.1f}% of your {category} budget.",
                        percentage=percentage
                    )
                    flash(f"📢 Budget Alert: You've used {percentage:.1f}% of your {category} budget.", "info")
    
    except Exception as e:
        flash(f"Error adding transaction: {str(e)}", "danger")
        return redirect(url_for('transaction.add_transaction_route'))

    return redirect(url_for('transaction.history'))


def handle_bulk_upload(user_id):
    """Handle bulk upload of transactions from CSV/Excel."""
    
    # Check if file was uploaded
    if 'file' not in request.files:
        flash("No file uploaded", "danger")
        return redirect(url_for('transaction.add_transaction_route'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash("No file selected", "danger")
        return redirect(url_for('transaction.add_transaction_route'))
    
    # Check file extension
    allowed_extensions = {'csv', 'xlsx', 'xls'}
    if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        flash("Only CSV, XLSX, and XLS files are allowed", "danger")
        return redirect(url_for('transaction.add_transaction_route'))
    
    try:
        # Read file based on extension
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        
        if file_ext == 'csv':
            transactions_data = parse_csv_file(file)
        elif file_ext in ['xlsx', 'xls']:
            transactions_data = parse_excel_file(file)
        
        # Process transactions
        added_count = 0
        error_count = 0
        errors = []
        
        for idx, txn in enumerate(transactions_data, 1):
            try:
                # Validate required fields
                if not txn.get('Date') or not txn.get('Description') or not txn.get('Amount'):
                    errors.append(f"Row {idx}: Missing required fields (Date, Description, or Amount)")
                    error_count += 1
                    continue
                
                # Parse data
                txn_date = str(txn['Date']).strip()
                description = str(txn['Description']).strip()
                
                try:
                    amount = float(txn['Amount'])
                except (ValueError, TypeError):
                    errors.append(f"Row {idx}: Invalid amount '{txn['Amount']}'")
                    error_count += 1
                    continue
                
                # Determine if expense or income
                txn_type = str(txn.get('Type', 'expense')).lower().strip()
                if txn_type not in ['expense', 'income']:
                    txn_type = 'expense'
                
                # Sanitize description
                description = sanitize_string(description, 255)
                
                # Auto-tag category for expenses
                if txn_type == 'expense':
                    category = predict_category(description)
                    is_auto_tagged = 1
                    amount = -abs(amount)  # Store as negative
                else:
                    category = 'Income'
                    is_auto_tagged = 0
                    amount = abs(amount)  # Store as positive
                
                # Add transaction
                add_transaction(
                    user_id=user_id,
                    amount=amount,
                    description=description,
                    category=category,
                    date=txn_date,
                    is_auto_tagged=is_auto_tagged
                )
                added_count += 1
                
            except Exception as e:
                errors.append(f"Row {idx}: {str(e)}")
                error_count += 1
        
        # Display results
        if added_count > 0:
            flash(f"✅ Successfully added {added_count} transaction(s)", "success")
        if error_count > 0:
            for error in errors[:5]:  # Show first 5 errors
                flash(f"⚠️ {error}", "warning")
            if len(errors) > 5:
                flash(f"... and {len(errors) - 5} more error(s)", "warning")
        
        return redirect(url_for('transaction.history'))
        
    except Exception as e:
        flash(f"Error processing file: {str(e)}", "danger")
        return redirect(url_for('transaction.add_transaction_route'))
@transaction_bp.route('/transactions/history')
def history():

    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    selected_month = request.args.get('month', None)
    
    # Get transactions grouped by month
    transactions_by_month = get_transactions_by_month(user_id, selected_month)
    
    # Get list of all available months for filter dropdown
    all_months = list(transactions_by_month.keys()) if not selected_month else None
    
    # Get monthly expense breakdown by category
    monthly_expenses = get_expense_by_month_and_category(user_id, selected_month)
    
    # Get selected month summary if a specific month is selected
    monthly_summary = None
    if selected_month:
        monthly_summary = get_monthly_summary(user_id, selected_month)
    
    return render_template(
        'history.html',
        transactions_by_month=transactions_by_month,
        monthly_expenses=monthly_expenses,
        all_months=all_months,
        selected_month=selected_month,
        monthly_summary=monthly_summary
    )


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




# -------- Parse CSV File --------
    """Parse CSV file and return list of transaction dicts."""
    transactions = []
    stream = io.TextIOWrapper(file.stream, encoding='utf-8')
    reader = csv.DictReader(stream)
    
    for row in reader:
        transactions.append(row)
    
    return transactions


def parse_excel_file(file):
    """Parse Excel file and return list of transaction dicts."""
    try:
        import openpyxl
    except ImportError:
        raise ImportError("openpyxl is required for Excel file support. Install with: pip install openpyxl")
    
    transactions = []
    workbook = openpyxl.load_workbook(file.stream)
    worksheet = workbook.active
    
    # Get headers from first row
    headers = []
    for cell in worksheet[1]:
        headers.append(cell.value)
    
    # Get data rows
    for row in worksheet.iter_rows(min_row=2, values_only=False):
        row_dict = {}
        for idx, cell in enumerate(row):
            if idx < len(headers):
                row_dict[headers[idx]] = cell.value
        transactions.append(row_dict)
    
    return transactions


# -------- Download CSV Template --------
@transaction_bp.route('/transactions/download-template')
def download_template():
    """Download a sample CSV template for bulk transaction upload."""
    
    # Create CSV data
    csv_data = io.StringIO()
    writer = csv.writer(csv_data)
    
    # Write header
    writer.writerow(['Date', 'Description', 'Amount', 'Type'])
    
    # Write sample rows
    writer.writerow(['2026-03-01', 'Grocery shopping', '45.50', 'expense'])
    writer.writerow(['2026-03-02', 'Monthly salary', '5000.00', 'income'])
    writer.writerow(['2026-03-03', 'Fuel for car', '60.00', 'expense'])
    writer.writerow(['2026-03-04', 'Restaurant dinner', '120.25', 'expense'])
    writer.writerow(['2026-03-05', 'Movie tickets', '25.00', 'expense'])
    
    # Create BytesIO and send
    csv_bytes = io.BytesIO(csv_data.getvalue().encode('utf-8'))
    csv_bytes.seek(0)
    
    return send_file(
        csv_bytes,
        mimetype='text/csv',
        as_attachment=True,
        download_name='transaction_template.csv'
    )
