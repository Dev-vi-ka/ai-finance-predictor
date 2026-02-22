import numpy as np
from sklearn.linear_model import LinearRegression
from models.transaction_model import get_monthly_expenses
from datetime import datetime
from dateutil.relativedelta import relativedelta

def predict_next_month_spending(user_id):
    """
    Fetches monthly expenses, trains a simple Linear Regression model,
    and predicts the spending for the next month.
    Returns a dictionary with labels, actual data, and the prediction.
    """
    monthly_data = get_monthly_expenses(user_id)

    # If not enough data, return empty/placeholder
    if not monthly_data:
        return {
            "labels": [],
            "actuals": [],
            "predicted_amount": 0,
            "prediction_month": ""
        }

    # Prepare data for ML
    # X: Month indices (0, 1, 2...)
    # y: Total expenses
    months = [entry['month'] for entry in monthly_data]
    expenses = [entry['total'] for entry in monthly_data]

    X = np.array(range(len(months))).reshape(-1, 1)
    y = np.array(expenses)

    # Train Model (Simple Linear Regression)
    # If we have only 1 point, we can't really regress, but let's handle it gracefully
    if len(months) < 2:
        predicted_amount = expenses[-1] # Naive prediction: same as last month
    else:
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next month (index = len(months))
        next_month_index = np.array([[len(months)]])
        predicted_amount = model.predict(next_month_index)[0]
    
    # Ensure prediction is not negative
    predicted_amount = max(0, predicted_amount)

    # Calculate next month label
    last_month_str = months[-1]
    last_month_date = datetime.strptime(last_month_str, "%Y-%m")
    next_month_date = last_month_date + relativedelta(months=1)
    next_month_str = next_month_date.strftime("%Y-%m")

    return {
        "labels": months,
        "actuals": expenses,
        "predicted_amount": round(predicted_amount, 2),
        "prediction_month": next_month_str
    }
