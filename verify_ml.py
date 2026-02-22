import sqlite3
import os
from ml.expense_predictor import predict_next_month_spending
from database.db_init import conn, cursor # Re-use init logic if we need to seed, but better to check existing data.

# We need to mock a user or assume one exists. 
# Let's check the database first.

DB_PATH = "database/finance.db"

def verify_prediction():
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check for users
    user = cursor.execute("SELECT * FROM users LIMIT 1").fetchone()
    if not user:
        print("No users found. Creating dummy user and transactions...")
        # Create dummy user
        cursor.execute("INSERT INTO users (name, email, password_hash) VALUES ('Test User', 'test@example.com', 'hash')")
        user_id = cursor.lastrowid
        
        # Create dummy transactions for last 3 months
        # Month 1: 1000
        # Month 2: 1200
        # Month 3: 1400
        # Expected Month 4: ~1600
        
        cursor.execute("INSERT INTO transactions (user_id, amount, date, type) VALUES (?, ?, ?, ?)", (user_id, -1000, '2023-01-15', 'expense'))
        # Wait, the schema uses amount < 0 for expense, but the model code uses ABS(amount) where amount < 0.
        # Let's check transaction_model.add_transaction
        # It stores incoming positive amount, but relies on caller to decide...
        # Wait, add_transaction takes `amount` and stores it. 
        # get_financial_summary checks for amount < 0 for expense.
        # So expenses should be stored as negative numbers?
        # Let's check transaction_routes.py
        # amount = abs(amount) ... wait.
        # if txn_type == 'expense' ... 
        # It calls add_transaction(..., amount=amount, ...)
        # It seems add_transaction just inserts what it gets.
        # But get_financial_summary queries `amount < 0`.
        # Converting `amount` to negative in add_transaction might be missing in `transaction_routes.py`?
        
        # Let's check `transaction_routes.py` again.
        # Line 37: amount = abs(amount).
        # It seems it ALWAYS stores positive amount? 
        # Then `get_financial_summary` checking `amount < 0` would fail?
        
        # Let's re-read transaction_routes.py carefully.
        pass

    else:
        user_id = user[0]
        print(f"Using existing user ID: {user_id}")

    conn.close()

    # Run Prediction
    try:
        result = predict_next_month_spending(user_id)
        print("Prediction Result:", result)
    except Exception as e:
        print("Error during prediction:", e)

if __name__ == "__main__":
    verify_prediction()
