# app/saam/interaction.py

import joblib
from textblob import TextBlob

from .cues import extract_cues
from .features import build_feature_vector
from .actions import select_action
from .personas import (
    silent_persona_reply,
    healthy_persona_reply,
    blocked_persona_reply
)

PERSONA_MAP = {
    "silent": silent_persona_reply,
    "healthy": healthy_persona_reply,
    "blocked": blocked_persona_reply
}

def sentiment_score(text: str) -> float:
    """
    Simple sentiment scoring using TextBlob polarity (-1 to +1).
    """
    return TextBlob(text).sentiment.polarity


def run_interaction_round(persona: str, raw_stats: dict, model_path="models/perceptron.pkl"):
    """
    Runs a single SAAM → Persona → Sentiment interaction cycle.
    """

    # Load model
    model = joblib.load(model_path)["model"]

    # 1. Extract cues
    cues = extract_cues(raw_stats)

    # 2. Build feature vector
    X = build_feature_vector(cues)

    # 3. Predict behavioural class
    pred = model.predict(X)[0]
    label_map = {0: "silent", 1: "healthy", 2: "blocked"}
    predicted_label = label_map[pred]

    # 4. Select SAAM action
    saam_action = select_action(predicted_label, cues)
    saam_message = saam_action["message"]

    # 5. Persona replies
    persona_fn = PERSONA_MAP[persona]
    persona_reply = persona_fn(saam_message)

    # 6. Sentiment score
    sentiment = sentiment_score(persona_reply)

    # 7. Return full interaction record
    return {
        "persona": persona,
        "predicted_label": predicted_label,
        "saam_message": saam_message,
        "persona_reply": persona_reply,
        "sentiment": sentiment,
        "cues": cues,
        "intervention_type": saam_action["intervention_type"],
        "action": saam_action["action"]
    }
