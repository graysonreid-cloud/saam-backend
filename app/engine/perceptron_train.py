# app/engine/perceptron_train.py

import joblib
import numpy as np
from sklearn.linear_model import Perceptron

from app.saam.features import FEATURE_ORDER

MODEL_PATH = "models/perceptron.pkl"

def train_perceptron(dataset):
    """
    Trains a multi-class perceptron using manually labelled data.
    Each row must contain:
      - user_id
      - features: list of feature values in FEATURE_ORDER
      - label: 0=silent, 1=healthy, 2=blocked
    """

    X = []
    y = []
    user_ids = []

    for row in dataset:
        X.append(row["features"])
        y.append(row["label"])
        user_ids.append(row["user_id"])

    X = np.array(X)
    y = np.array(y)

    model = Perceptron(max_iter=1000, tol=1e-3)
    model.fit(X, y)

    joblib.dump({
        "model": model,
        "feature_order": FEATURE_ORDER,
        "user_ids": user_ids
    }, MODEL_PATH)

    return model
