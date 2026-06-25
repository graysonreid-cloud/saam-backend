import joblib
import numpy as np

MODEL_PATH = "models/perceptron.pkl"

def load_model():
    data = joblib.load(MODEL_PATH)
    return data["model"]

def predict_label(stats: dict):
    clf = load_model()

    X = np.array([[
        stats.get("comments", 0),
        stats.get("assignments", 0),
        stats.get("transitions", 0)
    ]])

    pred = clf.predict(X)[0]
    return "healthy" if pred == 1 else "low_collaboration"
