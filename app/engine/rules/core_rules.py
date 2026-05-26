def apply_rules(state: dict):
    """
    Core team‑level rule engine.
    Evaluates normalised signals and emits intervention candidates.
    """

    interventions = []

    # Extract normalised signals
    participation = state.get("participation_norm", 0)
    imbalance = state.get("imbalance_norm", 0)
    blocker_age = state.get("blocker_age_norm", 0)
    owner_missing = state.get("blocker_owner_missing", False)
    time_urgency = state.get("time_remaining_norm", 0)
    missing_updates = state.get("missing_updates_norm", 0)

    # ----------------------------------------------------------------------
    # Declarative rule table
    # Each entry: (condition, name, category, priority, cue, message, explanation)
    # This keeps the rule engine compact, readable, and easy to extend.
    # ----------------------------------------------------------------------
    rules = [
        # Participation
        (
            participation < 0.25,
            "participation_critical_threshold",
            "participation",
            5,
            "critical_low_participation",
            "Participation is critically low — the team may be disengaged.",
            "Participation dropped below 25%, indicating widespread disengagement.",
        ),
        (
            0.25 <= participation < 0.45,
            "participation_low_threshold",
            "participation",
            3,
            "low_participation",
            "Participation seems low — consider inviting quieter members.",
            "Participation is below the healthy threshold of 45%.",
        ),

        # Dominance / talk‑time imbalance
        (
            imbalance > 0.75,
            "dominance_critical_threshold",
            "communication_dynamics",
            4,
            "dominant_voice",
            "One voice may be dominating — rebalance the discussion.",
            "Talk-time imbalance exceeded 75%, indicating dominance.",
        ),
        (
            0.55 < imbalance <= 0.75,
            "dominance_emerging_pattern",
            "communication_dynamics",
            2,
            "emerging_dominance",
            "A pattern of dominance is emerging — consider redirecting.",
            "Talk-time imbalance is above 55%, showing early dominance.",
        ),

        # Blocker age
        (
            blocker_age >= 0.8,
            "blocker_critical_age",
            "blockers",
            6,
            "critical_blocker",
            "A blocker has been unresolved for several days — escalate immediately.",
            "Blocker age indicates stalled progress.",
        ),
        (
            0.6 <= blocker_age < 0.8,
            "blocker_stale_age",
            "blockers",
            3,
            "stale_blocker",
            "A blocker is lingering — check if support is needed.",
            "Blocker age suggests slow resolution.",
        ),

        # Blocker owner missing
        (
            owner_missing,
            "blocker_missing_owner",
            "blockers",
            5,
            "missing_blocker_owner",
            "A blocker has no owner — assign responsibility.",
            "Blocker owner is missing, preventing resolution.",
        ),

        # Time pressure
        (
            time_urgency > 0.8,
            "standup_time_pressure",
            "ceremony",
            2,
            "time_pressure",
            "Time is nearly up — consider parking remaining discussions.",
            "Standup is close to exceeding its timebox.",
        ),

        # Reporting gaps
        (
            missing_updates == 1.0,
            "standup_reporting_gap",
            "ceremony",
            3,
            "reporting_gap",
            "Some team members did not provide full updates.",
            "Missing yesterday/today/blockers updates.",
        ),

        # Combined signals: psychological safety risk
        (
            participation < 0.3 and imbalance > 0.7,
            "psychological_safety_risk",
            "combined_signals",
            8,
            "team_silence_plus_dominance",
            "Low participation + dominance detected — rebalance the conversation.",
            "Combined signals indicate psychological safety issues.",
        ),
    ]

    # ----------------------------------------------------------------------
    # Evaluate rules
    # ----------------------------------------------------------------------
    for condition, name, category, priority, cue, message, explanation in rules:
        if condition:
            interventions.append({
                "rule_name": name,
                "rule_category": category,
                "rationale": None,  # placeholder for future reasoning engine
                "cue": cue,
                "message": message,
                "explanation": explanation,
                "priority": priority,
            })

    return interventions
