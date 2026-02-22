import sqlite3
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

DB_PATH = "database/finance.db"
MODEL_PATH = "ml/model.pkl"

def train_model():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Only train on expenses
    cursor.execute("""
        SELECT description, category 
        FROM transactions
        WHERE type='expense' AND category IS NOT NULL
    """)

    data = cursor.fetchall()
    conn.close()

    if len(data) < 5:
        print("Not enough data to train model.")
        return

    descriptions = [row[0] for row in data]
    categories = [row[1] for row in data]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(descriptions)

    model = LogisticRegression()
    model.fit(X, categories)

    with open(MODEL_PATH, "wb") as f:
        pickle.dump((model, vectorizer), f)

    print("Model trained and saved successfully.")


if __name__ == "__main__":
    train_model()
