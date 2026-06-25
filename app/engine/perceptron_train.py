import os
import numpy as np
from sklearn.linear_model import Perceptron
import joblib

MODEL_PATH = "models/perceptron.pkl"

def train_perceptron(training_data):
    # Ensure models directory exists
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    X = []
    y = []
    user_ids = []

    for row in training_data:
        X.append([
            row["comments"],
            row["assignments"],
            row["transitions"]
        ])
        y.append(row["label"])
        user_ids.append(row["user_id"])

    X = np.array(X)
    y = np.array(y)

    clf = Perceptron()
    clf.fit(X, y)

    joblib.dump({
        "model": clf,
        "user_ids": user_ids
    }, MODEL_PATH)

    return clf
