import sqlite3
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import GaussianNB, MultinomialNB
import numpy as np

DB_PATH = "database/finance.db"
MODEL_PATH = "ml/model.pkl"

def train_model():
    """Train category classifier model from transaction data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Only train on expenses (amount < 0) with valid categories
    cursor.execute("""
        SELECT description, category 
        FROM transactions
        WHERE amount < 0 AND category IS NOT NULL AND description IS NOT NULL
    """)

    data = cursor.fetchall()
    conn.close()

    if len(data) < 2:
        print("Not enough data to train model (need at least 2 samples).")
        return False

    descriptions = [row[0] for row in data]
    categories = [row[1] for row in data]

    try:
        # Use TF-IDF vectorization
        vectorizer = TfidfVectorizer(max_features=100, lowercase=True, stop_words='english')
        X = vectorizer.fit_transform(descriptions)
        
        # Use MultinomialNB for sparse data
        from sklearn.linear_model import LogisticRegression
        model = LogisticRegression(max_iter=200)
        model.fit(X, categories)

        # Save model and vectorizer
        os.makedirs("ml", exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump((model, vectorizer), f)

        print(f"✓ Category model trained on {len(data)} transactions.")
        return True
        
    except Exception as e:
        print(f"Error training model: {e}")
        return False


if __name__ == "__main__":
    train_model()
