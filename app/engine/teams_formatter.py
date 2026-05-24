def build_teams_message(decision: dict) -> str:
    """
    Builds a polished, standup‑specific Teams message for SAAM,
    including confidence interpretation and team health score.
    """

    message = decision.get("message", "")
    cue = decision.get("cue", "")
    explanation = decision.get("explanation", "")
    priority = decision.get("priority")
    confidence = decision.get("confidence")
    health = decision.get("team_health")

    # Priority → severity label
    if priority is not None:
        if priority >= 7:
            severity = "Critical"
        elif priority >= 5:
            severity = "High"
        elif priority >= 3:
            severity = "Moderate"
        else:
            severity = "Low"
    else:
        severity = "Info"

    # Confidence → natural language
    if confidence is not None:
        if confidence >= 0.8:
            confidence_text = "SAAM is highly confident in this assessment."
        elif confidence >= 0.6:
            confidence_text = "SAAM is moderately confident in this assessment."
        else:
            confidence_text = "SAAM has low confidence in this assessment."
    else:
        confidence_text = "Confidence unavailable."

    # Build final Teams message
    teams_message = (
        f"**Standup Insight — {severity} Priority**\n\n"
        f"{message}\n\n"
        f"**Why this matters:** {explanation}\n\n"
        f"**Signal detected:** `{cue}`\n\n"
        f"**Confidence:** {confidence_text}\n"
    )

    # Add health score cleanly
    if health is not None:
        teams_message += f"\n\n**Team Health Score:** {health}%\n"

    return teams_message
