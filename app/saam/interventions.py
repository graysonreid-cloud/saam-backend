# app/saam/interventions.py

INTERVENTION_MATRIX = {
    "silent": {
        "type": "soft",
        "action": "invite_contribution",
        "message": (
            "I noticed you’ve been quieter than usual. "
            "Would you like to share any updates or blockers?"
        )
    },

    "healthy": {
        "type": "none",
        "action": "reinforce_positive",
        "message": (
            "Great engagement and steady progress. "
            "Keep up the good collaboration."
        )
    },

    "blocked": {
        "type": "hard",
        "action": "escalate_blocker",
        "message": (
            "I see a blocker that has been open for a while. "
            "Let’s address it together or escalate if needed."
        )
    }
}
