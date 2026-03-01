import sqlite3
import os
from datetime import datetime, timedelta
from ml.expense_predictor import predict_next_month_spending

DB_PATH = "database/finance.db"

def verify_prediction():
    """Verify ML prediction functionality by creating test data if needed."""
    
    if not os.path.exists(DB_PATH):
        print("Database not found. Please run 'python database/db_init.py' first.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for existing users
    user = cursor.execute("SELECT * FROM users LIMIT 1").fetchone()
    if not user:
        print("Creating test user and transactions...")
        
        # Create test user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            ('Test User', 'test@example.com', 'hash123')
        )
        user_id = cursor.lastrowid
        
        # Create test transactions for last 3 months (stored as negative for expenses)
        base_date = datetime.now()
        amounts = [-1000, -1200, -1400]  # Progressive increase
        
        for i, amount in enumerate(amounts):
            month_date = base_date - timedelta(days=30 * (2 - i))
            date_str = month_date.strftime('%Y-%m-15')
            cursor.execute(
                "INSERT INTO transactions (user_id, amount, description, category, date) VALUES (?, ?, ?, ?, ?)",
                (user_id, amount, f"Test expense {i+1}", "Miscellaneous", date_str)
            )
        
        conn.commit()
        print(f"✓ Created test user (ID: {user_id}) with sample transactions")
    else:
        user_id = user[0]
        print(f"✓ Using existing user ID: {user_id}")

    conn.close()

    # Test the prediction
    print("\nRunning ML prediction...")
    try:
        result = predict_next_month_spending(user_id)
        
        if result['predicted_amount'] > 0:
            print(f"✓ Prediction successful!")
            print(f"  Forecast for {result['prediction_month']}: ₹{result['predicted_amount']:.2f}")
            print(f"  Historical data points: {len(result['actuals'])}")
        else:
            print("⚠ Prediction returned 0 (insufficient data)")
            print(f"  Available data: {result['labels']}")
            
    except Exception as e:
        print(f"✗ Error during prediction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_prediction()
