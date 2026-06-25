# app/saam/train.py

import joblib
from sklearn.linear_model import Perceptron
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

from .synthetic import generate_training_dataset

MODEL_PATH = "models/perceptron.pkl"

def train_saam_model(n_per_persona=200):
    """
    Train the multi-class SAAM model using synthetic cue-based data.
    """

    # 1. Generate dataset
    X, y = generate_training_dataset(n_per_persona=n_per_persona)

    # 2. Build training pipeline (scaler + perceptron)
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf", Perceptron(max_iter=1000, tol=1e-3))
    ])

    # 3. Train model
    pipeline.fit(X, y)

    # 4. Save model + metadata
    joblib.dump({
        "model": pipeline,
        "version": "1.1-multiclass-cues",
        "feature_order": [
            "participation_level",
            "talktime_imbalance",
            "blocker_age",
            "missing_updates",
            "blocker_owner_missing",
            "time_remaining",
            "goal_changes",
            "ceremony_type_encoded",
            "sentiment_score",
            "workload_ratio",
            "help_requests",
            "help_offers"
        ]
    }, MODEL_PATH)

    return pipeline
