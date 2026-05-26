def standup_rules(state):
    """
    Standup‑specific behavioural rules.
    Evaluates participation, dominance, blockers, reporting, and ceremony context.
    """

    decisions = []

    # Extract relevant standup signals
    participation = state.get("participation", 1.0)
    imbalance = state.get("talk_time_imbalance", 0.0)
    blocker_age = state.get("blocker_age_days", 0)
    missing_updates = state.get("missing_updates", False)
    time_remaining = state.get("time_remaining", 3)
    ceremony = state.get("ceremony")

    # ----------------------------------------------------------------------
    # Declarative rule table
    # Each entry: (condition, name, category, priority, cue, message, explanation)
    # This keeps the rule engine compact, readable, and easy to extend.
    # ----------------------------------------------------------------------
    rules = [
        (
            participation < 0.4,
            "standup_low_participation",
            "participation",
            7,
            "low_participation",
            "Participation is low — consider inviting quieter members to share updates.",
            f"Participation dropped to {participation:.2f}.",
        ),
        (
            imbalance > 0.6,
            "standup_dominance",
            "participation",
            8,
            "dominance_detected",
            "One or two members are dominating the standup — rebalance the flow.",
            f"Talk-time imbalance at {imbalance:.2f}.",
        ),
        (
            blocker_age >= 3,
            "standup_blocker_age",
            "blockers",
            9 if blocker_age >= 5 else 7,
            "blocker_age",
            "A blocker has been open for several days — escalate or support resolution.",
            f"Blocker age is {blocker_age} days.",
        ),
        (
            missing_updates,
            "standup_missing_updates",
            "reporting",
            6,
            "missing_updates",
            "Some team members did not provide updates — check if they need support.",
            "One or more members skipped updates.",
        ),
        (
            time_remaining <= 1,
            "standup_sprint_urgency",
            "planning",
            8,
            "sprint_urgency",
            "Sprint is nearly over — ensure focus on finishing committed work.",
            f"Only {time_remaining} days remain in the sprint.",
        ),
        (
            ceremony != "standup",
            "standup_off_topic",
            "meta",
            3,
            "off_topic",
            "This rule pack is for standups — ceremony mismatch detected.",
            f"Ceremony was {ceremony}.",
        ),
    ]

    # ----------------------------------------------------------------------
    # Evaluate rules
    # ----------------------------------------------------------------------
    for condition, name, category, priority, cue, message, explanation in rules:
        if condition:
            decisions.append({
                "rule_name": name,
                "rule_category": category,
                "priority": priority,
                "cue": cue,
                "message": message,
                "explanation": explanation,
            })

    return decisions
