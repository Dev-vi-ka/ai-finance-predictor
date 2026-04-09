import sqlite3
import pickle
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import numpy as np

# Use absolute path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "finance.db")
MODEL_PATH = os.path.join(BASE_DIR, "ml", "model.pkl")


def train_model():
    """Train category classifier model from transaction data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Train on ALL transactions with descriptions and categories
    cursor.execute("""
        SELECT description, category
        FROM transactions
        WHERE category IS NOT NULL
          AND description IS NOT NULL
          AND TRIM(description) != ''
          AND TRIM(category) != ''
    """)
    data = cursor.fetchall()
    conn.close()

    if len(data) < 2:
        print("Not enough data to train model (need at least 2 labelled transactions).")
        return False

    descriptions = [row[0].strip() for row in data]
    categories   = [row[1].strip() for row in data]
    unique_cats  = list(set(categories))

    print(f"Training on {len(data)} transactions across {len(unique_cats)} categories: {unique_cats}")

    try:
        if len(unique_cats) == 1:
            # Only one category — use a trivial classifier
            print(f"⚠ Only 1 category found ('{unique_cats[0]}'). Using passthrough model.")

            class SingleClassModel:
                def __init__(self, label):
                    self.label = label
                def predict(self, X):
                    return np.array([self.label] * X.shape[0])

            vectorizer = TfidfVectorizer(max_features=10)
            vectorizer.fit(["dummy"])
            model = SingleClassModel(unique_cats[0])

        else:
            # Full NLP pipeline: TF-IDF + Logistic Regression
            # LR generalises better than Random Forest on short text descriptions
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                lowercase=True,
                strip_accents='unicode',
                sublinear_tf=True,       # dampen effect of very frequent terms
            )
            classifier = LogisticRegression(
                max_iter=500,
                class_weight='balanced',
                C=1.0,
                solver='lbfgs',
            )

            X = vectorizer.fit_transform(descriptions)
            classifier.fit(X, categories)
            model = classifier

            # Quick cross-val score if we have enough data
            if len(data) >= 10:
                try:
                    cv_folds = min(5, len(unique_cats))
                    scores = cross_val_score(classifier, X, categories, cv=cv_folds, scoring='accuracy')
                    print(f"  Cross-val accuracy: {scores.mean()*100:.1f}% ± {scores.std()*100:.1f}%")
                except Exception:
                    pass  # cross-val not critical

        # Persist model + vectorizer together
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump((model, vectorizer), f)

        print(f"✓ Model saved → {MODEL_PATH}")
        return True

    except Exception as e:
        print(f"✗ Model training failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = train_model()
    if not success:
        print("\nTip: Add more labelled transactions (with descriptions and categories) first.")
