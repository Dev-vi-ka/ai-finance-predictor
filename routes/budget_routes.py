from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models.budget_model import (
    set_budget, get_budget, get_all_budgets, get_all_budget_status,
    get_category_spending, get_budget_usage_percentage, delete_budget
)
from models.alert_model import get_unread_alerts, get_all_alerts, mark_alert_as_read, get_unread_alert_count
from datetime import date

budget_bp = Blueprint(
    'budget',
    __name__,
    template_folder='../templates/budget'
)


# -------- Set Budget --------
@budget_bp.route('/budgets/set', methods=['GET', 'POST'])
def set_budget_route():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            category = request.form.get('category', '').strip()
            limit_amount = float(request.form.get('limit_amount', 0))
            month = request.form.get('month', date.today().strftime("%Y-%m"))
            
            if not category or limit_amount <= 0:
                flash("Please provide valid category and budget limit", "danger")
                return redirect(url_for('budget.set_budget_route'))
            
            set_budget(user_id, category, limit_amount, month)
            flash(f"Budget set for {category}: ${limit_amount:.2f}", "success")
            return redirect(url_for('budget.view_budgets'))
        
        except ValueError:
            flash("Invalid budget amount", "danger")
            return redirect(url_for('budget.set_budget_route'))
        except Exception as e:
            flash(f"Error setting budget: {str(e)}", "danger")
            return redirect(url_for('budget.set_budget_route'))
    
    current_month = date.today().strftime("%Y-%m")
    categories = [
        "Food", "Transport", "Utilities", "Entertainment", "Healthcare",
        "Shopping", "Dining", "Subscriptions", "Insurance", "Other"
    ]
    
    return render_template(
        'set_budget.html',
        categories=categories,
        current_month=current_month
    )


# -------- View All Budgets --------
@budget_bp.route('/budgets')
def view_budgets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    month = request.args.get('month', date.today().strftime("%Y-%m"))
    
    budgets = get_all_budget_status(user_id, month)
    
    return render_template(
        'budgets.html',
        budgets=budgets,
        month=month,
        current_month=date.today().strftime("%Y-%m")
    )


# -------- Edit Budget --------
@budget_bp.route('/budgets/<int:budget_id>/edit', methods=['GET', 'POST'])
def edit_budget(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    if request.method == 'POST':
        try:
            limit_amount = float(request.form.get('limit_amount', 0))
            if limit_amount <= 0:
                flash("Budget limit must be greater than 0", "danger")
            else:
                set_budget(user_id, request.form.get('category'), limit_amount)
                flash("Budget updated successfully", "success")
            return redirect(url_for('budget.view_budgets'))
        except ValueError:
            flash("Invalid budget amount", "danger")
            return redirect(url_for('budget.view_budgets'))
    
    return redirect(url_for('budget.view_budgets'))


# -------- Delete Budget --------
@budget_bp.route('/budgets/<int:budget_id>/delete', methods=['POST'])
def delete_budget_route(budget_id):
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    try:
        delete_budget(user_id, budget_id)
        flash("Budget deleted successfully", "success")
    except Exception as e:
        flash(f"Error deleting budget: {str(e)}", "danger")
    
    return redirect(url_for('budget.view_budgets'))


# -------- API: Get Budget Status --------
@budget_bp.route('/api/budgets/status')
def get_budget_status_api():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    month = request.args.get('month', date.today().strftime("%Y-%m"))
    
    budgets = get_all_budget_status(user_id, month)
    
    return jsonify({
        'success': True,
        'budgets': budgets
    })


# -------- Alerts: View All --------
@budget_bp.route('/alerts')
def view_alerts():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    alerts = get_all_alerts(user_id)
    
    return render_template('alerts.html', alerts=alerts)


# -------- Alerts: Get Unread Count (API) --------
@budget_bp.route('/api/alerts/count')
def get_alert_count():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    count = get_unread_alert_count(user_id)
    
    return jsonify({'count': count})


# -------- Alerts: Mark as Read --------
@budget_bp.route('/alerts/<int:alert_id>/read', methods=['POST'])
def mark_alert_read(alert_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    try:
        mark_alert_as_read(alert_id, user_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -------- Budget Overview (for Dashboard) --------
@budget_bp.route('/api/budget-overview')
def get_budget_overview():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    
    budgets = get_all_budget_status(user_id)
    alert_count = get_unread_alert_count(user_id)
    
    critical_budgets = [b for b in budgets if b['status'] == 'Critical']
    warning_budgets = [b for b in budgets if b['status'] == 'Warning']
    
    return jsonify({
        'success': True,
        'total_budgets': len(budgets),
        'critical_count': len(critical_budgets),
        'warning_count': len(warning_budgets),
        'unread_alerts': alert_count,
        'budgets': budgets
    })
