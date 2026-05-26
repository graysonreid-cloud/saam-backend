def build_teams_message(best: dict) -> str:
    """
    Build a clean, human‑readable Teams message for SAAM interventions.
    Handles both single‑cue and multi‑cue composite rules.
    """

    rule_name = best.get("rule_name", "")
    message = best.get("message", "")
    explanation = best.get("explanation", "")
    priority = best.get("priority", "")
    confidence = best.get("confidence", 0)
    team_health = best.get("team_health", 0)
    standup_reasoning = best.get("standup_reasoning", "")

    # --- 1. Header ----------------------------------------------------------
    header = "**SAAM Intervention**"

    # --- 2. Cue / signal section -------------------------------------------
    if rule_name == "multi_cue_composite":
        cue_section = "**Multiple issues detected**"

        # List contributing rule messages (not rule names)
        contributing = best.get("contributing_rules", [])
        if contributing:
            cue_section += "\n" + "\n".join(f"- {msg}" for msg in contributing)
    else:
        cue = best.get("cue", "")
        cue_section = f"**Signal detected:** {cue}"

    # --- 3. Main intervention message --------------------------------------
    main_message = f"**Intervention:** {message}"

    # --- 4. Explanation -----------------------------------------------------
    explanation_section = f"**Reasoning Summary:**\n{explanation}"

    # --- 5. Behavioural interpretation (standup reasoning) ------------------
    reasoning_section = (
        f"**Behavioural Interpretation:**\n{standup_reasoning}"
        if standup_reasoning else ""
    )

    # --- 6. Confidence + team health ---------------------------------------
    confidence_pct = int(confidence * 100)
    health_pct = int(team_health)

    meta_section = (
        f"**Confidence:** {confidence_pct}%\n"
        f"**Team Health:** {health_pct}/100"
    )

    # --- 7. Priority --------------------------------------------------------
    priority_section = f"**Priority:** {priority}"

    # --- 8. Final assembly --------------------------------------------------
    parts = [
        header,
        cue_section,
        main_message,
        explanation_section,
        reasoning_section,
        meta_section,
        priority_section,
    ]

    # Remove empty blocks
    parts = [p for p in parts if p.strip()]

    return "\n\n".join(parts)
