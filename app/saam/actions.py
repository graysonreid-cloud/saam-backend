# app/saam/actions.py

from app.saam.interventions import INTERVENTION_MATRIX

def select_action(predicted_label: str, cues: dict) -> dict:
    """
    Given the model's predicted label and the extracted cues,
    return the appropriate SAAM action.
    Now includes sprint‑aware rules layered on top of the matrix.
    """

    # -----------------------------------------------------
    # SPRINT‑AWARE RULES (override matrix when triggered)
    # -----------------------------------------------------
    days_remaining = cues.get("days_remaining")
    sprint_progress = cues.get("sprint_progress")
    issue_age = cues.get("issue_age_days")
    blocker_age = cues.get("blocker_age")

    # 1. End‑of‑sprint risk escalation
    if days_remaining is not None and issue_age is not None:
        if days_remaining <= 2 and issue_age >= 3:
            return {
                "label": predicted_label,
                "intervention_type": "escalate",
                "action": "highlight_risk",
                "message": (
                    "This issue has been open for several days and the sprint "
                    "is nearly over. It may need attention."
                ),
                "cues": cues
            }

    # 2. Silent behaviour late in sprint
    if sprint_progress is not None:
        if sprint_progress > 0.7 and cues.get("participation_level", 1) == 0:
            return {
                "label": predicted_label,
                "intervention_type": "soft",
                "action": "invite_contribution",
                "message": (
                    "We’re late in the sprint and I haven’t seen many updates "
                    "from you. Anything you'd like to share?"
                ),
                "cues": cues
            }

    # 3. Blocker older than remaining sprint time
    if blocker_age and days_remaining:
        if blocker_age > days_remaining:
            return {
                "label": predicted_label,
                "intervention_type": "escalate",
                "action": "escalate_blocker",
                "message": (
                    "This blocker has been open longer than the time left in "
                    "the sprint. It may need escalation."
                ),
                "cues": cues
            }

    # -----------------------------------------------------
    # FALLBACK: MATRIX‑BASED INTERVENTION
    # -----------------------------------------------------
    if predicted_label not in INTERVENTION_MATRIX:
        return {
            "label": predicted_label,
            "intervention_type": "none",
            "action": "unknown",
            "message": "No intervention available for this state.",
            "cues": cues
        }

    intervention = INTERVENTION_MATRIX[predicted_label]

    return {
        "label": predicted_label,
        "intervention_type": intervention["type"],
        "action": intervention["action"],
        "message": intervention["message"],
        "cues": cues
    }
