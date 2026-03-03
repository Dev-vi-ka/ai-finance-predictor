import sqlite3
from config import DATABASE_PATH
from datetime import datetime, timedelta
from collections import defaultdict

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================
# A. AGGREGATED METRICS
# ============================================

def get_total_users():
    """Get total number of registered users."""
    conn = get_db_connection()
    result = conn.execute("SELECT COUNT(*) as total FROM users").fetchone()
    conn.close()
    return result['total'] if result else 0


def get_active_users(days=30):
    """Get number of users active in the last N days."""
    conn = get_db_connection()
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    result = conn.execute("""
        SELECT COUNT(DISTINCT user_id) as active 
        FROM transactions 
        WHERE date >= ?
    """, (cutoff_date,)).fetchone()
    conn.close()
    return result['active'] if result else 0


def get_average_monthly_spending():
    """Get average monthly spending across all users."""
    conn = get_db_connection()
    result = conn.execute("""
        SELECT 
            AVG(monthly_spending) as avg_spending
        FROM (
            SELECT 
                user_id,
                SUM(amount) as monthly_spending
            FROM transactions
            WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
            GROUP BY user_id
        )
    """).fetchone()
    conn.close()
    return round(result['avg_spending'] if result['avg_spending'] else 0, 2)


def get_average_savings_rate():
    """Get average savings rate across all users."""
    conn = get_db_connection()
    
    # This assumes income data is stored. If not available, calculate from user data
    result = conn.execute("""
        SELECT 
            AVG(savings_rate) as avg_rate
        FROM (
            SELECT 
                user_id,
                CASE 
                    WHEN SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) > 0
                    THEN (SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) - 
                          SUM(CASE WHEN amount < 0 THEN ABS(amount) ELSE 0 END)) / 
                         SUM(CASE WHEN amount > 0 THEN amount ELSE 0 END) * 100
                    ELSE 0
                END as savings_rate
            FROM transactions
            WHERE strftime('%Y-%m', date) = strftime('%Y-%m', 'now')
            GROUP BY user_id
        )
        WHERE savings_rate > 0
    """).fetchone()
    conn.close()
    return round(result['avg_rate'] if result['avg_rate'] else 0, 2)


def get_category_distribution():
    """Get aggregated expense distribution by category."""
    conn = get_db_connection()
    result = conn.execute("""
        SELECT 
            category,
            COUNT(*) as count,
            ROUND(SUM(amount), 2) as total_amount,
            ROUND(AVG(amount), 2) as avg_amount,
            ROUND(100.0 * SUM(amount) / (SELECT SUM(amount) FROM transactions WHERE amount > 0), 2) as percentage
        FROM transactions
        WHERE amount > 0 AND category IS NOT NULL
        GROUP BY category
        ORDER BY total_amount DESC
    """).fetchall()
    conn.close()
    return [dict(row) for row in result] if result else []


def get_user_retention_metrics(days=30):
    """Calculate user retention metrics."""
    conn = get_db_connection()
    
    current_date = datetime.now()
    previous_period_start = current_date - timedelta(days=days*2)
    previous_period_end = current_date - timedelta(days=days)
    current_period_start = current_date - timedelta(days=days)
    
    # Users active in previous period
    prev_active = conn.execute("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM transactions
        WHERE date >= ? AND date <= ?
    """, (previous_period_start.strftime('%Y-%m-%d'), 
          previous_period_end.strftime('%Y-%m-%d'))).fetchone()
    
    # Users active in both periods
    retained = conn.execute("""
        SELECT COUNT(DISTINCT user_id) as count
        FROM (
            SELECT DISTINCT user_id FROM transactions
            WHERE date >= ? AND date <= ?
            INTERSECT
            SELECT DISTINCT user_id FROM transactions
            WHERE date >= ? AND date <= ?
        )
    """, (previous_period_start.strftime('%Y-%m-%d'),
          previous_period_end.strftime('%Y-%m-%d'),
          current_period_start.strftime('%Y-%m-%d'),
          current_date.strftime('%Y-%m-%d'))).fetchone()
    
    conn.close()
    
    prev_count = prev_active['count'] if prev_active else 0
    retained_count = retained['count'] if retained else 0
    
    retention_rate = (retained_count / prev_count * 100) if prev_count > 0 else 0
    
    return {
        'previous_active': prev_count,
        'retained': retained_count,
        'retention_rate': round(retention_rate, 2)
    }


# ============================================
# B. TREND ANALYSIS
# ============================================

def get_category_growth_trends(months=3):
    """Get expense trends by category over the last N months."""
    conn = get_db_connection()
    
    trends = []
    for i in range(months, -1, -1):
        month_date = (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m')
        result = conn.execute("""
            SELECT 
                category,
                ROUND(SUM(amount), 2) as total
            FROM transactions
            WHERE strftime('%Y-%m', date) = ? AND amount > 0
            GROUP BY category
        """, (month_date,)).fetchall()
        
        month_data = {month_date: {dict(row)['category']: dict(row)['total'] for row in result}}
        trends.append(month_data)
    
    # Calculate growth rates
    growth_analysis = defaultdict(lambda: {'months_data': [], 'growth_rate': 0})
    
    if len(trends) > 1:
        current_month = trends[-1]
        previous_month = trends[-2]
        
        for cat in current_month[list(current_month.keys())[0]]:
            current_val = current_month[list(current_month.keys())[0]].get(cat, 0)
            previous_val = previous_month[list(previous_month.keys())[0]].get(cat, 0)
            
            if previous_val > 0:
                growth_rate = ((current_val - previous_val) / previous_val) * 100
            else:
                growth_rate = 100 if current_val > 0 else 0
            
            growth_analysis[cat] = {
                'current_month': current_val,
                'previous_month': previous_val,
                'growth_rate': round(growth_rate, 2),
                'growth_status': 'increasing' if growth_rate > 0 else 'decreasing'
            }
    
    conn.close()
    return dict(growth_analysis)


def get_seasonal_trends(current_month=None):
    """Identify seasonal spending patterns."""
    if not current_month:
        current_month = datetime.now().month
    
    conn = get_db_connection()
    
    # Get data for the same month over the last 2-3 years
    seasonal_data = conn.execute("""
        SELECT 
            category,
            ROUND(AVG(monthly_total), 2) as avg_spending,
            ROUND(MAX(monthly_total), 2) as peak_spending,
            COUNT(*) as occurrences
        FROM (
            SELECT 
                category,
                strftime('%Y', date) as year,
                strftime('%m', date) as month,
                SUM(amount) as monthly_total
            FROM transactions
            WHERE strftime('%m', date) = ? AND amount > 0
            GROUP BY category, year, month
        )
        GROUP BY category
        ORDER BY avg_spending DESC
    """, (f"{current_month:02d}",)).fetchall()
    
    conn.close()
    return [dict(row) for row in seasonal_data] if seasonal_data else []


def get_spending_spikes_analysis(threshold_percentile=75):
    """Identify spending spikes and anomalies."""
    conn = get_db_connection()
    
    spikes = conn.execute("""
        SELECT 
            user_id,
            category,
            COUNT(*) as spike_count,
            ROUND(AVG(amount), 2) as avg_amount,
            ROUND(MAX(amount), 2) as max_amount,
            date
        FROM (
            SELECT 
                user_id,
                category,
                amount,
                date,
                ROW_NUMBER() OVER (PARTITION BY user_id, category ORDER BY amount DESC) as rank
            FROM transactions
            WHERE amount > 0 AND category IS NOT NULL
        )
        WHERE rank <= 3
        GROUP BY user_id, category
        HAVING spike_count > 2
        ORDER BY max_amount DESC
        LIMIT 10
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in spikes] if spikes else []


# ============================================
# C. MODEL PERFORMANCE DASHBOARD
# ============================================

def get_model_performance_summary():
    """Get latest ML model performance metrics."""
    conn = get_db_connection()
    
    metrics = conn.execute("""
        SELECT 
            metric_type,
            value,
            metadata,
            created_at
        FROM ml_model_metrics
        ORDER BY created_at DESC
        LIMIT 4
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in metrics] if metrics else []


def calculate_categorization_accuracy():
    """Calculate model categorization accuracy based on auto-tagged vs corrected."""
    conn = get_db_connection()
    
    total_auto_tagged = conn.execute("""
        SELECT COUNT(*) as count FROM transactions WHERE is_auto_tagged = 1
    """).fetchone()['count']
    
    corrections = conn.execute("""
        SELECT COUNT(*) as count FROM model_corrections
    """).fetchone()['count']
    
    conn.close()
    
    if total_auto_tagged == 0:
        return 0
    
    accuracy = ((total_auto_tagged - corrections) / total_auto_tagged) * 100
    return round(accuracy, 2)


def calculate_user_correction_rate():
    """Calculate the percentage of auto-tagged transactions that users corrected."""
    conn = get_db_connection()
    
    total_auto_tagged = conn.execute("""
        SELECT COUNT(*) as count FROM transactions WHERE is_auto_tagged = 1
    """).fetchone()['count']
    
    corrections = conn.execute("""
        SELECT COUNT(*) as count FROM model_corrections
    """).fetchone()['count']
    
    conn.close()
    
    if total_auto_tagged == 0:
        return 0
    
    correction_rate = (corrections / total_auto_tagged) * 100
    return round(correction_rate, 2)


def get_model_prediction_errors():
    """Get prediction error metrics by category."""
    conn = get_db_connection()
    
    errors = conn.execute("""
        SELECT 
            original_category,
            corrected_category,
            COUNT(*) as error_count
        FROM model_corrections
        GROUP BY original_category, corrected_category
        ORDER BY error_count DESC
        LIMIT 15
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in errors] if errors else []


def detect_model_drift(lookback_days=30):
    """Detect model drift by comparing recent vs historical performance."""
    conn = get_db_connection()
    
    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    # Recent corrections
    recent = conn.execute("""
        SELECT COUNT(*) as count FROM model_corrections
        WHERE created_at >= ?
    """, (cutoff_date,)).fetchone()['count']
    
    # Recent auto-tagged
    recent_auto_tagged = conn.execute("""
        SELECT COUNT(*) as count FROM transactions
        WHERE is_auto_tagged = 1 AND created_at >= ?
    """, (cutoff_date,)).fetchone()['count']
    
    # Historical corrections
    historical = conn.execute("""
        SELECT COUNT(*) as count FROM model_corrections
    """).fetchone()['count']
    
    # Historical auto-tagged
    historical_auto_tagged = conn.execute("""
        SELECT COUNT(*) as count FROM transactions
        WHERE is_auto_tagged = 1
    """).fetchone()['count']
    
    conn.close()
    
    recent_error_rate = (recent / recent_auto_tagged * 100) if recent_auto_tagged > 0 else 0
    historical_error_rate = (historical / historical_auto_tagged * 100) if historical_auto_tagged > 0 else 0
    
    drift = round(recent_error_rate - historical_error_rate, 2)
    drift_status = 'concerning' if drift > 5 else 'stable' if drift > -5 else 'improving'
    
    return {
        'recent_error_rate': round(recent_error_rate, 2),
        'historical_error_rate': round(historical_error_rate, 2),
        'drift_value': drift,
        'drift_status': drift_status,
        'lookback_days': lookback_days
    }


def get_most_misclassified_categories():
    """Get categories that are most frequently misclassified."""
    conn = get_db_connection()
    
    misclassified = conn.execute("""
        SELECT 
            original_category as category,
            COUNT(*) as error_count,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM model_corrections), 2) as error_percentage
        FROM model_corrections
        GROUP BY original_category
        ORDER BY error_count DESC
    """).fetchall()
    
    conn.close()
    return [dict(row) for row in misclassified] if misclassified else []


# ============================================
# COMBINED DASHBOARD DATA
# ============================================

def get_admin_dashboard_data():
    """Get all data needed for the admin dashboard."""
    return {
        'aggregated_metrics': {
            'total_users': get_total_users(),
            'active_users': get_active_users(),
            'avg_monthly_spending': get_average_monthly_spending(),
            'avg_savings_rate': get_average_savings_rate(),
            'category_distribution': get_category_distribution(),
            'retention_metrics': get_user_retention_metrics(),
        },
        'trend_analysis': {
            'category_growth': get_category_growth_trends(),
            'seasonal_trends': get_seasonal_trends(),
            'spending_spikes': get_spending_spikes_analysis(),
        },
        'model_performance': {
            'accuracy': calculate_categorization_accuracy(),
            'correction_rate': calculate_user_correction_rate(),
            'prediction_errors': get_model_prediction_errors(),
            'drift_detection': detect_model_drift(),
            'misclassified_categories': get_most_misclassified_categories(),
            'performance_summary': get_model_performance_summary(),
        }
    }


def log_model_metric(metric_type, value, metadata=None):
    """Log a model performance metric."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO ml_model_metrics (metric_type, value, metadata)
        VALUES (?, ?, ?)
    """, (metric_type, value, metadata))
    conn.commit()
    conn.close()


def log_model_correction(user_id, transaction_id, original_category, corrected_category):
    """Log a user correction to the model."""
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO model_corrections (user_id, transaction_id, original_category, corrected_category)
        VALUES (?, ?, ?, ?)
    """, (user_id, transaction_id, original_category, corrected_category))
    conn.commit()
    conn.close()
