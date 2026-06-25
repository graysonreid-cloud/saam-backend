from app.saam.cues import extract_cues
from app.saam.features import build_feature_vector
from app.saam.actions import select_action
import joblib

model = joblib.load("models/perceptron.pkl")["model"]

raw = {
    "participation_level": 0.1,
    "talktime_imbalance": 0.8,
    "blocker_age": 1,
    "missing_updates": True,
    "blocker_owner_missing": False,
    "time_remaining": 5,
    "goal_changes": 0,
    "ceremony_type": "standup",
    "sentiment_score": -0.1,
    "workload_ratio": 0.9,
    "help_requests": 0,
    "help_offers": 0
}

cues = extract_cues(raw)
X = build_feature_vector(cues)
pred = model.predict(X)[0]
label_map = {0: "silent", 1: "healthy", 2: "blocked"}
label = label_map[pred]

action = select_action(label, cues)

print("Prediction:", label)
print("Action:", action)
