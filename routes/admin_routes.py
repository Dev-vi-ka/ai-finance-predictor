from flask import Blueprint, render_template, session, redirect, url_for, jsonify, request
from config import ADMIN_EMAILS
from models.user_model import get_user_by_id
from models.admin_model import (
    get_admin_dashboard_data,
    get_total_users,
    get_active_users,
    get_average_monthly_spending,
    get_average_savings_rate,
    get_category_distribution,
    get_user_retention_metrics,
    get_category_growth_trends,
    get_seasonal_trends,
    get_spending_spikes_analysis,
    calculate_categorization_accuracy,
    calculate_user_correction_rate,
    get_model_prediction_errors,
    detect_model_drift,
    get_most_misclassified_categories,
)

admin_bp = Blueprint(
    'admin',
    __name__,
    url_prefix='/admin',
    template_folder='../templates/admin'
)

# ===============================================
# ADMIN AUTHENTICATION MIDDLEWARE
# ===============================================

def require_admin():
    """Decorator to check if user is admin."""
    def decorator(f):
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            # Check if user is admin by email
            user = get_user_by_id(session.get('user_id'))
            if not user or user['email'] not in ADMIN_EMAILS:
                return redirect(url_for('dashboard.index'))
            
            return f(*args, **kwargs)
        decorated_function.__name__ = f.__name__
        return decorated_function
    return decorator


# ===============================================
# MAIN ADMIN DASHBOARD
# ===============================================

@admin_bp.route('/dashboard')
@require_admin()
def dashboard():
    """Main admin dashboard with overview of all metrics."""
    data = get_admin_dashboard_data()
    
    return render_template(
        'dashboard.html',
        metrics=data['aggregated_metrics'],
        trends=data['trend_analysis'],
        model_performance=data['model_performance'],
        page_title='Admin Dashboard'
    )


# ===============================================
# A. AGGREGATED METRICS ROUTES
# ===============================================

@admin_bp.route('/metrics/aggregated')
@require_admin()
def aggregated_metrics():
    """Display aggregated metrics section."""
    retention = get_user_retention_metrics()
    
    return render_template(
        'metrics/aggregated.html',
        total_users=get_total_users(),
        active_users=get_active_users(),
        avg_monthly_spending=get_average_monthly_spending(),
        avg_savings_rate=get_average_savings_rate(),
        category_distribution=get_category_distribution(),
        retention_rate=retention['retention_rate'],
        retained_users=retention['retained'],
        previous_active=retention['previous_active'],
        page_title='Aggregated Metrics'
    )


@admin_bp.route('/api/metrics/summary')
@require_admin()
def get_metrics_summary():
    """API endpoint to get metrics summary as JSON."""
    return jsonify({
        'total_users': get_total_users(),
        'active_users': get_active_users(),
        'avg_monthly_spending': get_average_monthly_spending(),
        'avg_savings_rate': get_average_savings_rate(),
        'category_distribution': get_category_distribution(),
        'retention': get_user_retention_metrics(),
    })


# ===============================================
# B. TREND ANALYSIS ROUTES
# ===============================================

@admin_bp.route('/trends')
@require_admin()
def trends():
    """Display trend analysis section."""
    category_growth = get_category_growth_trends(months=6)
    seasonal = get_seasonal_trends()
    spikes = get_spending_spikes_analysis()
    
    # Calculate top growing categories
    top_growing = sorted(
        category_growth.items(),
        key=lambda x: x[1]['growth_rate'],
        reverse=True
    )[:5]
    
    return render_template(
        'metrics/trends.html',
        category_growth=dict(top_growing),
        seasonal_trends=seasonal,
        spending_spikes=spikes,
        page_title='Trend Analysis'
    )


@admin_bp.route('/api/trends/category-growth')
@require_admin()
def get_category_growth():
    """Get category growth data as JSON."""
    months = request.args.get('months', 6, type=int)
    growth = get_category_growth_trends(months=months)
    return jsonify(growth)


@admin_bp.route('/api/trends/seasonal')
@require_admin()
def get_seasonal_data():
    """Get seasonal trend data as JSON."""
    month = request.args.get('month', None, type=int)
    seasonal = get_seasonal_trends(current_month=month)
    return jsonify([dict(row) if isinstance(row, dict) else row for row in seasonal])


# ===============================================
# C. MODEL PERFORMANCE ROUTES
# ===============================================

@admin_bp.route('/model-performance')
@require_admin()
def model_performance():
    """Display model performance dashboard."""
    accuracy = calculate_categorization_accuracy()
    correction_rate = calculate_user_correction_rate()
    prediction_errors = get_model_prediction_errors()
    drift = detect_model_drift()
    misclassified = get_most_misclassified_categories()
    
    # Determine model health status
    if accuracy >= 90:
        model_status = 'healthy'
    elif accuracy >= 75:
        model_status = 'acceptable'
    else:
        model_status = 'needs_attention'
    
    return render_template(
        'metrics/model_performance.html',
        accuracy=accuracy,
        correction_rate=correction_rate,
        prediction_errors=prediction_errors,
        drift_detection=drift,
        misclassified_categories=misclassified,
        model_status=model_status,
        page_title='Model Performance Dashboard'
    )


@admin_bp.route('/api/model/performance')
@require_admin()
def get_model_performance():
    """Get model performance data as JSON."""
    return jsonify({
        'accuracy': calculate_categorization_accuracy(),
        'correction_rate': calculate_user_correction_rate(),
        'prediction_errors': get_model_prediction_errors(),
        'drift_detection': detect_model_drift(),
        'misclassified_categories': get_most_misclassified_categories(),
    })


@admin_bp.route('/api/model/drift')
@require_admin()
def get_drift_data():
    """Get drift detection data as JSON."""
    days = request.args.get('days', 30, type=int)
    drift = detect_model_drift(lookback_days=days)
    return jsonify(drift)


# ===============================================
# REAL-TIME MONITORING
# ===============================================

@admin_bp.route('/monitoring')
@require_admin()
def monitoring():
    """Real-time monitoring dashboard."""
    data = get_admin_dashboard_data()
    
    return render_template(
        'monitoring.html',
        data=data,
        page_title='Real-time Monitoring'
    )


@admin_bp.route('/api/monitoring/live')
@require_admin()
def live_monitoring_data():
    """Get live monitoring data for real-time updates."""
    import json
    
    # Get critical insights
    accuracy = calculate_categorization_accuracy()
    correction_rate = calculate_user_correction_rate()
    drift = detect_model_drift()
    
    alerts = []
    
    # Generate alerts based on metrics
    if accuracy < 75:
        alerts.append({
            'level': 'critical',
            'message': f'Model accuracy dropped to {accuracy}%. Please review.',
            'metric': 'accuracy'
        })
    
    if drift['drift_status'] == 'concerning':
        alerts.append({
            'level': 'warning',
            'message': f'Model drift detected: {drift["drift_value"]}% change in error rate.',
            'metric': 'drift'
        })
    
    if correction_rate > 15:
        alerts.append({
            'level': 'warning',
            'message': f'High correction rate: {correction_rate}%. Users are frequently correcting categories.',
            'metric': 'corrections'
        })
    
    return jsonify({
        'accuracy': accuracy,
        'correction_rate': correction_rate,
        'drift': drift,
        'active_users': get_active_users(),
        'total_users': get_total_users(),
        'alerts': alerts,
        'timestamp': str(datetime.now())
    })


# ===============================================
# ANALYTICS & REPORTS
# ===============================================

@admin_bp.route('/analytics')
@require_admin()
def analytics():
    """Advanced analytics and reporting."""
    return render_template(
        'analytics.html',
        page_title='Advanced Analytics'
    )


@admin_bp.route('/reports/export')
@require_admin()
def export_report():
    """Export admin report as JSON or CSV."""
    import json
    from datetime import datetime
    
    format_type = request.args.get('format', 'json')
    data = get_admin_dashboard_data()
    
    if format_type == 'json':
        return jsonify(data)
    elif format_type == 'csv':
        # TODO: Implement CSV export
        return jsonify({'error': 'CSV export coming soon'})
    
    return jsonify({'error': 'Invalid format'})


from datetime import datetime
