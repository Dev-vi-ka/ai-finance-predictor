import pickle
import os

MODEL_PATH = "ml/model.pkl"

def predict_category(description):

    if not os.path.exists(MODEL_PATH):
        return "Miscellaneous"

    with open(MODEL_PATH, "rb") as f:
        model, vectorizer = pickle.load(f)

    X = vectorizer.transform([description])
    prediction = model.predict(X)

    return prediction[0]
