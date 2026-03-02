import sqlite3
from config import DATABASE_PATH
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# -------- Create Alert --------
def create_alert(user_id, alert_type, category, title, message, percentage=None, data=None):
    """Create an in-app alert.
    
    Args:
        user_id: User ID
        alert_type: Type of alert ('budget_warning', 'budget_exceeded', 'budget_critical')
        category: Expense category
        title: Alert title
        message: Alert message
        percentage: Budget usage percentage
        data: Additional JSON data
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts 
        (user_id, alert_type, category, title, message, percentage, data, is_read, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, 0, CURRENT_TIMESTAMP)
    """, (user_id, alert_type, category, title, message, percentage, data))
    
    conn.commit()
    alert_id = cursor.lastrowid
    conn.close()
    
    return alert_id


# -------- Get Unread Alerts --------
def get_unread_alerts(user_id):
    """Get all unread alerts for a user."""
    conn = get_db_connection()
    alerts = conn.execute(
        """SELECT * FROM alerts 
           WHERE user_id = ? AND is_read = 0 
           ORDER BY created_at DESC""",
        (user_id,)
    ).fetchall()
    conn.close()
    return alerts


# -------- Get All Alerts --------
def get_all_alerts(user_id, limit=50):
    """Get all alerts for a user."""
    conn = get_db_connection()
    alerts = conn.execute(
        """SELECT * FROM alerts 
           WHERE user_id = ? 
           ORDER BY created_at DESC 
           LIMIT ?""",
        (user_id, limit)
    ).fetchall()
    conn.close()
    return alerts


# -------- Mark Alert as Read --------
def mark_alert_as_read(alert_id, user_id):
    """Mark alert as read."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE alerts SET is_read = 1 WHERE id = ? AND user_id = ?",
        (alert_id, user_id)
    )
    conn.commit()
    conn.close()


# -------- Mark All As Read --------
def mark_all_alerts_as_read(user_id):
    """Mark all alerts as read for a user."""
    conn = get_db_connection()
    conn.execute(
        "UPDATE alerts SET is_read = 1 WHERE user_id = ?",
        (user_id,)
    )
    conn.commit()
    conn.close()


# -------- Delete Alert --------
def delete_alert(alert_id, user_id):
    """Delete an alert."""
    conn = get_db_connection()
    conn.execute(
        "DELETE FROM alerts WHERE id = ? AND user_id = ?",
        (alert_id, user_id)
    )
    conn.commit()
    conn.close()


# -------- Get Alert Count --------
def get_unread_alert_count(user_id):
    """Get count of unread alerts."""
    conn = get_db_connection()
    result = conn.execute(
        "SELECT COUNT(*) as count FROM alerts WHERE user_id = ? AND is_read = 0",
        (user_id,)
    ).fetchone()
    conn.close()
    return result['count'] if result else 0


# -------- Check if Alert Already Exists --------
def alert_exists_today(user_id, alert_type, category):
    """Check if similar alert already created today to avoid duplicates."""
    conn = get_db_connection()
    result = conn.execute(
        """SELECT id FROM alerts 
           WHERE user_id = ? AND alert_type = ? AND category = ? 
           AND date(created_at) = date('now')""",
        (user_id, alert_type, category)
    ).fetchone()
    conn.close()
    return result is not None
