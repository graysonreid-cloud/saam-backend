# app/api/saam_action.py

from fastapi import APIRouter
import joblib

from app.saam.cues import extract_cues
from app.saam.features import build_feature_vector
from app.saam.actions import select_action

router = APIRouter()

MODEL_PATH = "models/perceptron.pkl"

def load_model():
    data = joblib.load(MODEL_PATH)
    return data["model"]

@router.post("/saam/action")
def saam_action(raw_stats: dict):
    """
    SAAM Action Endpoint:
    - Extract cues
    - Build feature vector
    - Predict behavioural class
    - Select intervention
    """

    # 1. Extract cues
    cues = extract_cues(raw_stats)

    # 2. Build feature vector
    X = build_feature_vector(cues)

    # 3. Load trained model
    model = load_model()

    # 4. Predict class
    pred_class = model.predict(X)[0]

    label_map = {
        0: "silent",
        1: "healthy",
        2: "blocked"
    }
    predicted_label = label_map.get(pred_class, "unknown")

    # 5. Select intervention
    action = select_action(predicted_label, cues)

    return {
        "prediction": predicted_label,
        "action": action
    }
