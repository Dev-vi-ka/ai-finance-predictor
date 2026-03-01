"""Data preprocessing utilities for ML models."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def clean_description(description):
    """Clean and normalize transaction descriptions."""
    if not description:
        return "Unknown"
    
    # Convert to lowercase and strip whitespace
    cleaned = description.strip().lower()
    
    # Remove special characters but keep alphanumeric and spaces
    cleaned = ''.join(c if c.isalnum() or c.isspace() else '' for c in cleaned)
    
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    
    return cleaned or "Unknown"


def normalize_amount(amount):
    """Normalize transaction amounts to absolute value."""
    return abs(float(amount))


def get_date_features(date_str):
    """Extract useful date features for analysis."""
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        date = datetime.now()
    
    return {
        'year': date.year,
        'month': date.month,
        'day': date.day,
        'quarter': (date.month - 1) // 3 + 1,
        'day_of_week': date.weekday(),
        'is_weekend': date.weekday() >= 5
    }


def categorize_spending_level(amount, threshold_low=1000, threshold_high=5000):
    """Classify spending amount as Low/Medium/High."""
    if amount < threshold_low:
        return "Low"
    elif amount < threshold_high:
        return "Medium"
    else:
        return "High"


def remove_outliers(amounts, std_dev_threshold=2):
    """Remove statistical outliers from amount list."""
    if len(amounts) < 2:
        return amounts
    
    mean = np.mean(amounts)
    std = np.std(amounts)
    
    # Keep only values within threshold standard deviations
    cleaned = [a for a in amounts if abs(a - mean) <= std_dev_threshold * std]
    
    return cleaned if cleaned else amounts


def prepare_time_series(transactions):
    """Convert transaction data to time series format."""
    if not transactions:
        return pd.DataFrame()
    
    df = pd.DataFrame(transactions)
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].abs()
    
    # Sort by date
    df = df.sort_values('date')
    
    return df
