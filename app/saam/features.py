# app/saam/features.py

import numpy as np

FEATURE_ORDER = [
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

def build_feature_vector(cues: dict) -> np.ndarray:
    """
    Convert cue dictionary into a consistent numpy feature vector.
    """
    vector = []

    for key in FEATURE_ORDER:
        value = cues.get(key, 0)
        vector.append(float(value))

    return np.array([vector])  # 2D array for sklearn
