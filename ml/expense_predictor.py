import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from models.transaction_model import get_monthly_expenses
from datetime import datetime
from dateutil.relativedelta import relativedelta

def predict_next_month_spending(user_id):
    """
    Fetches monthly expenses, extracts time-series features (month, moving average, trend),
    trains a Gradient Boosting model, and predicts the spending for the next month.
    """
    monthly_data = get_monthly_expenses(user_id)

    if not monthly_data:
        return {
            "labels": [],
            "actuals": [],
            "predicted_amount": 0.0,
            "prediction_month": ""
        }

    months = [entry['month'] for entry in monthly_data]
    expenses = [entry['total'] for entry in monthly_data]

    # Calculate next month date
    last_month_str = months[-1]
    last_month_date = datetime.strptime(last_month_str, "%Y-%m")
    next_month_date = last_month_date + relativedelta(months=1)
    next_month_str = next_month_date.strftime("%Y-%m")

    # If too little data, fallback to naive heuristics
    if len(months) < 3:
        avg_expense = sum(expenses) / len(expenses)
        predicted_amount = avg_expense
    else:
        # Advanced Feature Engineering
        df = pd.DataFrame({"month": months, "expense": expenses})
        df["month_obj"] = pd.to_datetime(df["month"], format="%Y-%m")
        df["month_num"] = df["month_obj"].dt.month
        df["time_idx"] = np.arange(len(df))
        
        # Calculate trailing features (shifting to avoid data leakage)
        df["prev_expense"] = df["expense"].shift(1).fillna(df["expense"].mean())
        df["moving_avg_3"] = df["expense"].rolling(window=3, min_periods=1).mean().shift(1).fillna(df["expense"].mean())
        
        features = ["time_idx", "month_num", "prev_expense", "moving_avg_3"]
        
        X = df[features]
        y = df["expense"]
        
        # Train advanced model
        model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
        model.fit(X, y)
        
        # Prepare next month features
        next_time_idx = len(df)
        next_month_num = next_month_date.month
        next_prev_expense = expenses[-1]
        next_moving_avg_3 = np.mean(expenses[-3:]) if len(expenses) >= 3 else np.mean(expenses)
        
        X_next = pd.DataFrame([[next_time_idx, next_month_num, next_prev_expense, next_moving_avg_3]], columns=features)
        
        # Predict
        predicted_amount = model.predict(X_next)[0]
    
    # Ensure prediction is reasonable (not negative, and smooth out extreme leaps if sparse data)
    predicted_amount = max(0, predicted_amount)
    
    # If the prediction heavily deviates upward on tiny datasets, dampen it slightly
    mean_historical = np.mean(expenses)
    if len(months) < 6 and predicted_amount > mean_historical * 2:
        predicted_amount = mean_historical + (predicted_amount - mean_historical) * 0.5 

    return {
        "labels": months,
        "actuals": expenses,
        "predicted_amount": round(float(predicted_amount), 2),
        "prediction_month": next_month_str
    }
