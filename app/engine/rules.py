def apply_rules(state: dict):
    interventions = []

    # Helper: safe getter with default
    def get(key, default=None):
        return state.get(key, default)

    participation = get("participation", 0)
    talk_time_imbalance = get("talk_time_imbalance", 0)
    blocker_age_days = get("blocker_age_days", 0)
    blocker_owner_missing = get("blocker_owner_missing", False)
    ceremony = (get("ceremony") or "").lower()
    time_remaining = get("time_remaining", 999)

    # ---------------------------------------------------------
    # 1. PARTICIPATION HEALTH
    # ---------------------------------------------------------
    if participation < 0.25:
        interventions.append({
            "rule_name": "participation_critical_threshold",
            "rule_category": "participation",
            "rule_version": "1.0",
            "rationale": "Critical participation levels indicate disengagement and psychological safety risks.",
            "cue": "critical_low_participation",
            "message": "Participation is critically low — the team may be disengaged.",
            "explanation": "Participation dropped below 25%, indicating widespread disengagement.",
            "priority": 5
        })

    elif participation < 0.45:
        interventions.append({
            "rule_name": "participation_low_threshold",
            "rule_category": "participation",
            "rule_version": "1.0",
            "rationale": "Low participation suggests uneven engagement and potential communication issues.",
            "cue": "low_participation",
            "message": "Participation seems low — consider inviting quieter members.",
            "explanation": "Participation is below the healthy threshold of 45%.",
            "priority": 3
        })

    # ---------------------------------------------------------
    # 2. DOMINANCE / TALK-TIME IMBALANCE
    # ---------------------------------------------------------
    if talk_time_imbalance > 0.75:
        interventions.append({
            "rule_name": "dominance_critical_threshold",
            "rule_category": "communication_dynamics",
            "rule_version": "1.0",
            "rationale": "High dominance suppresses team voice and reduces psychological safety.",
            "cue": "dominant_voice",
            "message": "One voice may be dominating — rebalance the discussion.",
            "explanation": "Talk-time imbalance exceeded 75%, indicating dominance.",
            "priority": 4
        })

    elif talk_time_imbalance > 0.55:
        interventions.append({
            "rule_name": "dominance_emerging_pattern",
            "rule_category": "communication_dynamics",
            "rule_version": "1.0",
            "rationale": "Emerging dominance patterns should be corrected early to maintain balance.",
            "cue": "emerging_dominance",
            "message": "A pattern of dominance is emerging — consider redirecting.",
            "explanation": "Talk-time imbalance is above 55%, showing early dominance.",
            "priority": 2
        })

    # ---------------------------------------------------------
    # 3. BLOCKER AGE
    # ---------------------------------------------------------
    if blocker_age_days >= 5:
        interventions.append({
            "rule_name": "blocker_critical_age",
            "rule_category": "blockers",
            "rule_version": "1.0",
            "rationale": "Long-standing blockers indicate stalled progress and require escalation.",
            "cue": "critical_blocker",
            "message": "A blocker has been unresolved for 5+ days — escalate immediately.",
            "explanation": "Blocker age exceeded 5 days, indicating stalled progress.",
            "priority": 6
        })

    elif blocker_age_days >= 2:
        interventions.append({
            "rule_name": "blocker_stale_age",
            "rule_category": "blockers",
            "rule_version": "1.0",
            "rationale": "Stale blockers slow down delivery and should be addressed proactively.",
            "cue": "stale_blocker",
            "message": "A blocker is lingering — check if support is needed.",
            "explanation": "Blocker age is above 2 days, suggesting slow resolution.",
            "priority": 3
        })

    # ---------------------------------------------------------
    # 4. BLOCKER OWNER MISSING
    # ---------------------------------------------------------
    if blocker_owner_missing:
        interventions.append({
            "rule_name": "blocker_missing_owner",
            "rule_category": "blockers",
            "rule_version": "1.0",
            "rationale": "Blockers without owners cannot be resolved and require immediate assignment.",
            "cue": "missing_blocker_owner",
            "message": "A blocker has no owner — assign responsibility.",
            "explanation": "Blocker owner is missing, preventing resolution.",
            "priority": 5
        })

    # ---------------------------------------------------------
    # 5. CEREMONY-SPECIFIC RULES
    # ---------------------------------------------------------
    if ceremony == "daily":
        if time_remaining < 2:
            interventions.append({
                "rule_name": "daily_overrun",
                "rule_category": "ceremony",
                "rule_version": "1.0",
                "rationale": "Daily Scrum should remain timeboxed; overruns reduce focus.",
                "cue": "daily_overrun",
                "message": "Daily is running long — consider parking discussions.",
                "explanation": "Time remaining is under 2 minutes in a Daily Scrum.",
                "priority": 4
            })

    if ceremony == "retro":
        if participation < 0.4:
            interventions.append({
                "rule_name": "retro_low_engagement",
                "rule_category": "ceremony",
                "rule_version": "1.0",
                "rationale": "Retrospectives require high engagement to be effective.",
                "cue": "retro_silence",
                "message": "Retro engagement is low — try a structured activity.",
                "explanation": "Participation is below 40% during a retrospective.",
                "priority": 5
            })

    if ceremony == "planning":
        if blocker_age_days > 0:
            interventions.append({
                "rule_name": "planning_blocker_carryover",
                "rule_category": "ceremony",
                "rule_version": "1.0",
                "rationale": "Active blockers may affect sprint commitments and should be reviewed.",
                "cue": "planning_blocker_carryover",
                "message": "A blocker may affect sprint planning — address before committing.",
                "explanation": "Planning ceremony detected with active blockers.",
                "priority": 4
            })

    # ---------------------------------------------------------
    # 6. TEAM HEALTH SIGNALS (COMBINED)
    # ---------------------------------------------------------
    if participation < 0.3 and talk_time_imbalance > 0.7:
        interventions.append({
            "rule_name": "psychological_safety_risk",
            "rule_category": "combined_signals",
            "rule_version": "1.0",
            "rationale": "Low participation + dominance indicates psychological safety issues.",
            "cue": "team_silence_plus_dominance",
            "message": "Low participation + dominance detected — rebalance the conversation.",
            "explanation": "Combined signals indicate psychological safety issues.",
            "priority": 7
        })

    return interventions
