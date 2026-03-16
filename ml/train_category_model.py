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
        unique_categories = list(set(categories))
        
        from sklearn.pipeline import Pipeline
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.linear_model import LogisticRegression
        
        # If all transactions share exactly the same category, ML algorithms will crash 
        # because they require >= 2 classes. We must handle this gracefully!
        if len(unique_categories) == 1:
            print(f"Warning: Only 1 unique category found '{unique_categories[0]}'. Cannot train full ML model. Generating fallback model.")
            # Dummy model that always predicts the single class
            class DummyModel:
                def __init__(self, single_class):
                    self.single_class = single_class
                def predict(self, X):
                    import numpy as np
                    return np.array([self.single_class] * X.shape[0])
            
            vectorizer = TfidfVectorizer(max_features=10)
            vectorizer.fit(["dummy text"]) # fit on dummy text so it doesn't fail on transform
            model = DummyModel(unique_categories[0])
            
        else:
            # Full advanced NLP classification pipeline
            vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2), lowercase=True, stop_words='english')
            
            # Use Random Forest for robust text categorization based on description keywords
            classifier = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
            
            X = vectorizer.fit_transform(descriptions)
            model = classifier
            model.fit(X, categories)

        # Save model and vectorizer
        os.makedirs("ml", exist_ok=True)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump((model, vectorizer), f)

        print(f"✓ Category model trained on {len(data)} transactions.")
        return True
        
    except Exception as e:
        print(f"Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    train_model()
