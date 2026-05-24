def apply_rules(state: dict):
    interventions = []

    # Helper: safe getter with default
    def get(key, default=None):
        return state.get(key, default)

    # Extract standup-relevant signals
    participation = get("participation", 0)
    talk_time_imbalance = get("talk_time_imbalance", 0)
    blocker_age_days = get("blocker_age_days", 0)
    blocker_owner_missing = get("blocker_owner_missing", False)
    time_remaining = get("time_remaining", 999)
    missing_updates = get("missing_updates", False)

    # ---------------------------------------------------------
    # 1. PARTICIPATION HEALTH
    # ---------------------------------------------------------
    if participation < 0.25:
        interventions.append({
            "rule_name": "participation_critical_threshold",
            "rule_category": "participation",
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
            "rationale": "Blockers without owners cannot be resolved and require immediate assignment.",
            "cue": "missing_blocker_owner",
            "message": "A blocker has no owner — assign responsibility.",
            "explanation": "Blocker owner is missing, preventing resolution.",
            "priority": 5
        })

    # ---------------------------------------------------------
    # 5. CRITICAL: BLOCKER UNOWNED + AGED
    # ---------------------------------------------------------
    if blocker_owner_missing and blocker_age_days >= 5:
        interventions.append({
            "rule_name": "blocker_unowned_and_aged",
            "rule_category": "blockers",
            "rationale": "An old, unowned blocker is a critical flow risk requiring immediate escalation.",
            "cue": "blocker_unowned_aged",
            "message": "A blocker is old and unowned — escalate immediately.",
            "explanation": "Blocker age exceeded 5 days and no owner is assigned.",
            "priority": 7
        })

    # ---------------------------------------------------------
    # 6. TIME PRESSURE (Standup Timebox)
    # ---------------------------------------------------------
    if time_remaining < 2:
        interventions.append({
            "rule_name": "standup_time_pressure",
            "rule_category": "ceremony",
            "rationale": "Standups should remain timeboxed; overruns reduce focus and flow.",
            "cue": "time_pressure",
            "message": "Time is nearly up — consider parking remaining discussions.",
            "explanation": f"Only {time_remaining} minutes left in the standup.",
            "priority": 2
        })

    # ---------------------------------------------------------
    # 7. REPORTING GAPS (Yesterday/Today/Blockers)
    # ---------------------------------------------------------
    if missing_updates:
        interventions.append({
            "rule_name": "standup_reporting_gap",
            "rule_category": "ceremony",
            "rationale": "Missing updates reduce transparency and hinder flow-based decision-making.",
            "cue": "reporting_gap",
            "message": "Some team members did not provide full updates.",
            "explanation": "Missing yesterday/today/blockers updates.",
            "priority": 3
        })

    # ---------------------------------------------------------
    # 8. TEAM HEALTH SIGNALS (COMBINED)
    # ---------------------------------------------------------
    if participation < 0.3 and talk_time_imbalance > 0.7:
        interventions.append({
            "rule_name": "psychological_safety_risk",
            "rule_category": "combined_signals",
            "rationale": "Low participation + dominance indicates psychological safety issues.",
            "cue": "team_silence_plus_dominance",
            "message": "Low participation + dominance detected — rebalance the conversation.",
            "explanation": "Combined signals indicate psychological safety issues.",
            "priority": 8
        })

    return interventions
