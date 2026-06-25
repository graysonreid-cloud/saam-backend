# app/saam/actions.py

from app.saam.interventions import INTERVENTION_MATRIX

def select_action(predicted_label: str, cues: dict) -> dict:
    """
    Given the model's predicted label and the extracted cues,
    return the appropriate SAAM action.
    """

    if predicted_label not in INTERVENTION_MATRIX:
        return {
            "type": "none",
            "action": "unknown",
            "message": "No intervention available for this state."
        }

    intervention = INTERVENTION_MATRIX[predicted_label]

    return {
        "label": predicted_label,
        "intervention_type": intervention["type"],
        "action": intervention["action"],
        "message": intervention["message"],
        "cues": cues  # included for logging & analysis
    }
