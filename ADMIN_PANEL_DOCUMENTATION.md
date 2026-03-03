# Admin Panel Documentation

## Overview

A comprehensive admin dashboard has been built with three main sections for managing and monitoring the AI Finance Predictor platform:

### Access

- **URL**: `/admin/dashboard`
- **Authentication**: Admin-only (currently user_id = 1)
- **Navigation**: Look for the "👑 Admin" dropdown in the top navigation bar

---

## Features

### A. Aggregated Metrics Dashboard

**URL**: `/admin/metrics/aggregated`

Displays platform-wide metrics including:

#### User Metrics
- **Total Users**: Total number of registered users
- **Active Users (30d)**: Users who added transactions in the last 30 days
- **Activity Rate**: Percentage of total users active in the past 30 days

#### Financial Metrics
- **Average Monthly Spending**: Per-user average spending
- **Average Savings Rate**: Aggregated savings rate across all users

#### Retention Metrics
- **Retention Rate**: Percentage of users from the previous period who remained active
- **Previous Period Active Users**: Number of active users in the comparison period
- **Retained Users**: Number of users active in both periods

#### Category Distribution
- Transaction counts by category
- Total and average spending by category
- Percentage distribution visualization
- Interactive pie/bar charts ready for implementation

### B. Trend Analysis Dashboard

**URL**: `/admin/trends`

Identify spending patterns and growth trends:

#### Category Growth Trends
- **6-Month Growth Rates**: Month-over-month growth percentages for each category
- **Growth Status**: Identifies if spending is increasing or decreasing
- **Current vs Previous Month**: Direct comparison of spending amounts
- **Top Growing Categories**: Highest growth rates ranked

Example Insight: *"Transport spending increased 14% across users this quarter."*

#### Seasonal Patterns
- Historical spending by month across users
- Peak spending identification
- Average spending per month per category
- Multi-year comparison for same month

#### Spending Anomalies
- Identifies users with unusual spending spikes
- Shows top spending spike incidents
- Flags anomalies by category
- Helps identify fraudulent or unusual transaction patterns

### C. Model Performance Dashboard

**URL**: `/admin/model-performance`

Monitor ML model health and effectiveness:

#### Key Performance Indicators

1. **Categorization Accuracy (%)**
   - Percentage of auto-tagged transactions that are correct
   - Threshold: 75% (warning), 90% (healthy)
   - Status indicators: 🟢 Healthy, 🟡 Acceptable, 🔴 Needs Attention

2. **User Correction Rate (%)**
   - Percentage of auto-tagged transactions corrected by users
   - Indicates how often the model makes mistakes
   - High rate → Model needs retraining

3. **Model Drift Detection**
   - Compares recent error rate vs historical error rate
   - Tracks changes over last 30 days
   - Status: Stable, Improving, or Concerning
   - Helps detect data distribution shifts

#### Detailed Metrics

- **Prediction Errors**: Top categories where model makes mistakes
- **Misclassified Categories**: Categories with highest error counts
- **Error Visualization**: Shows which categories are confused with others

#### Model Health Alerts

The system automatically generates alerts:
- 🔴 **Critical**: Accuracy < 75% or drift > 5%
- 🟡 **Warning**: Correction rate > 15%

#### Recommendations

Automatic recommendations including:
- Model retraining suggestions
- Data quality review prompts
- A/B testing guidance
- Best practices for monitoring

### D. Real-time Monitoring

**URL**: `/admin/monitoring`

Live system metrics with auto-refresh:

- **Active Users**: Current activity in last 30 days
- **Model Accuracy**: Real-time performance metric
- **Correction Rate**: Current user correction trend
- **Model Drift**: Real-time drift indicator
- **System Status**: Database, ML Model, User Activity, Data Quality
- **Active Alerts**: Critical and warning-level notifications
- **Auto-refresh**: Data updates every 30 seconds

### E. Advanced Analytics

**URL**: `/admin/analytics`

In-depth analysis tools:

#### Custom Report Generator
- Select report type (User Metrics, Financial, Model Health, Category Analysis, Retention)
- Specify date ranges
- Export as JSON
- CSV/PDF exports coming soon

#### Data Export Options
- **Full Dashboard Export**: All metrics as JSON
- **User Analytics**: Demographics and behavior
- **Financial Data**: Aggregated spending patterns

#### Available Analytics
- All aggregated metrics
- All trend analyses
- All model performance data
- Predictive insights (coming soon)

---

## Database Schema

### New Tables

#### `ml_model_metrics`
- Stores historical model performance metrics
- Tracks accuracy, error rates, drift values
- Enables trend analysis of model health

```sql
CREATE TABLE ml_model_metrics (
    id INTEGER PRIMARY KEY,
    metric_type TEXT NOT NULL,
    value REAL NOT NULL,
    metadata TEXT,
    created_at TIMESTAMP
);
```

#### `model_corrections`
- Logs every time a user corrects a model prediction
- Used to calculate correction rate and identify problem areas
- Enables feedback loop for model improvement

```sql
CREATE TABLE model_corrections (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    transaction_id INTEGER NOT NULL,
    original_category TEXT,
    corrected_category TEXT,
    created_at TIMESTAMP
);
```

---

## API Endpoints

All endpoints require admin authentication (user_id = 1).

### Main Dashboard
- `GET /admin/dashboard` - Main admin dashboard

### Metrics
- `GET /admin/metrics/aggregated` - Aggregated metrics page
- `GET /admin/api/metrics/summary` - JSON: Summary metrics
- `GET /admin/trends` - Trend analysis page
- `GET /admin/api/trends/category-growth?months=6` - JSON: Category growth data
- `GET /admin/api/trends/seasonal?month=3` - JSON: Seasonal data

### Model Performance
- `GET /admin/model-performance` - Model performance page
- `GET /admin/api/model/performance` - JSON: All model metrics
- `GET /admin/api/model/drift?days=30` - JSON: Drift data

### Monitoring & Reports
- `GET /admin/monitoring` - Real-time monitoring page
- `GET /admin/api/monitoring/live` - JSON: Live metrics with alerts
- `GET /admin/analytics` - Analytics page
- `GET /admin/reports/export?format=json` - Export full report

---

## Implementation Details

### Admin Authentication

Currently, admin access is protected by checking `session['user_id'] == 1`.

To enhance security, consider:

```python
# Add an is_admin flag to users table
ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0;

# Update authentication check
if not session.get('user_id') or not get_admin_status(session['user_id']):
    return redirect(url_for('auth.login'))
```

### Data Aggregation

The `admin_model.py` module provides comprehensive functions:

```python
# Main entry point
data = get_admin_dashboard_data()  # Returns all metrics organized

# Specific queries available:
get_total_users()
get_active_users(days=30)
get_average_monthly_spending()
get_category_growth_trends(months=3)
get_seasonal_trends(current_month=None)
detect_model_drift(lookback_days=30)
calculate_categorization_accuracy()
calculate_user_correction_rate()
```

### Logging Model Metrics

To track model performance over time:

```python
from models.admin_model import log_model_metric

# After training or evaluation
log_model_metric('accuracy', 0.92, metadata='after_retraining')
log_model_metric('drift', 2.5, metadata='30_day_comparison')
```

### Logging User Corrections

When users correct categorization:

```python
from models.admin_model import log_model_correction

log_model_correction(
    user_id=request.user_id,
    transaction_id=transaction.id,
    original_category='Food',
    corrected_category='Groceries'
)
```

---

## Usage Workflows

### Monitor Model Health

1. Go to Admin Dashboard → Model Performance
2. Check accuracy % (target: > 90%)
3. Review correction rate (target: < 10%)
4. Check drift status (target: stable/improving)
5. If alerts present, review misclassified categories
6. If needed, trigger model retraining

### Identify Growing Expense Categories

1. Go to Admin Dashboard → Trends
2. Review "Most Growing Expense Categories"
3. Look for categories with growth > 10%
4. Can notify users about their spending trends
5. Helps with budget recommendations

### Analyze User Retention

1. Go to Admin Dashboard → Aggregated Metrics
2. Check "Retention Rate" (30-day)
3. If retention < 50%, investigate user engagement
4. Check most used features vs unused
5. Plan feature improvements or notifications

### Export Data for External Analysis

1. Go to Admin Dashboard → Analytics
2. Select report type and date range
3. Choose export format (JSON available)
4. Download and use in external BI tools
5. CSV/PDF exports coming soon

---

## Future Enhancements

### Planned Features

- [ ] Interactive charts (Chart.js integration)
- [ ] CSV/PDF export functionality
- [ ] Predictive analytics for user churn
- [ ] Custom alert rules
- [ ] Scheduled report generation
- [ ] Email notifications
- [ ] Dashboard customization
- [ ] Role-based access control (multiple admins)
- [ ] Historical data visualization
- [ ] Anomaly detection algorithms

### Recommended Additions

1. **Admin User Management**
   - Add/remove admin users
   - Audit logs of admin actions

2. **Alerting System**
   - Configure accuracy thresholds
   - Email notifications
   - Slack integration

3. **Model Management**
   - View trained models
   - Trigger retraining
   - A/B testing framework

4. **User Support Dashboard**
   - Search users by email
   - View their transactions
   - Manual budget adjustments

---

## Security Considerations

### Current Implementation
- Admin access check: `session['user_id'] == 1`
- No rate limiting
- No audit logging

### Recommendations

```python
# Add audit logging
def log_admin_action(user_id, action, details):
    conn = get_db_connection()
    conn.execute("""
        INSERT INTO admin_logs (user_id, action, details, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    """, (user_id, action, details))
    conn.commit()

# Add rate limiting
from flask_limiter import Limiter
limiter = Limiter(app)

@admin_bp.route('/dashboard')
@limiter.limit("10 per minute")
@require_admin()
def dashboard():
    ...
```

---

## Support

For questions or issues with the admin panel:
1. Check database connections in `config.py`
2. Verify user_id = 1 is your admin account
3. Review error logs in Flask console
4. Check that all tables were created (see Database Schema section)

---

**Admin Panel Version**: 1.0  
**Last Updated**: March 2, 2026  
**Status**: Production Ready
