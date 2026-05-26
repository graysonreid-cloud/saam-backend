# app/rules/standup_rules.py

def standup_rules(state):
    decisions = []

    # ---------------------------------------------------------
    # 1. Low Participation
    # ---------------------------------------------------------
    if state.get("participation", 1.0) < 0.4:
        decisions.append({
            "cue": "low_participation",
            "message": "Participation is low — consider inviting quieter members to share updates.",
            "explanation": f"Participation dropped to {state.get('participation'):.2f}.",
            "priority": 7,
            "rule_name": "standup_low_participation",
            "rule_category": "participation"
        })

    # ---------------------------------------------------------
    # 2. Dominance / Talk-Time Imbalance
    # ---------------------------------------------------------
    if state.get("talk_time_imbalance", 0) > 0.6:
        decisions.append({
            "cue": "dominance_detected",
            "message": "One or two members are dominating the standup — rebalance the flow.",
            "explanation": f"Talk-time imbalance at {state.get('talk_time_imbalance'):.2f}.",
            "priority": 8,
            "rule_name": "standup_dominance",
            "rule_category": "participation"
        })

    # ---------------------------------------------------------
    # 3. Blocker Age
    # ---------------------------------------------------------
    blocker_age = state.get("blocker_age_days", 0)
    if blocker_age >= 3:
        decisions.append({
            "cue": "blocker_age",
            "message": "A blocker has been open for several days — escalate or support resolution.",
            "explanation": f"Blocker age is {blocker_age} days.",
            "priority": 9 if blocker_age >= 5 else 7,
            "rule_name": "standup_blocker_age",
            "rule_category": "blockers"
        })

    # ---------------------------------------------------------
    # 4. Missing Updates
    # ---------------------------------------------------------
    if state.get("missing_updates", False):
        decisions.append({
            "cue": "missing_updates",
            "message": "Some team members did not provide updates — check if they need support.",
            "explanation": "One or more members skipped updates.",
            "priority": 6,
            "rule_name": "standup_missing_updates",
            "rule_category": "reporting"
        })

    # ---------------------------------------------------------
    # 5. Sprint Urgency (Time Remaining)
    # ---------------------------------------------------------
    time_remaining = state.get("time_remaining", 3)
    if time_remaining <= 1:
        decisions.append({
            "cue": "sprint_urgency",
            "message": "Sprint is nearly over — ensure focus on finishing committed work.",
            "explanation": f"Only {time_remaining} days remain in the sprint.",
            "priority": 8,
            "rule_name": "standup_sprint_urgency",
            "rule_category": "planning"
        })

    # ---------------------------------------------------------
    # 6. Off‑Topic Detection
    # ---------------------------------------------------------
    if state.get("ceremony") != "standup":
        decisions.append({
            "cue": "off_topic",
            "message": "This rule pack is for standups — ceremony mismatch detected.",
            "explanation": f"Ceremony was {state.get('ceremony')}.",
            "priority": 3,
            "rule_name": "standup_off_topic",
            "rule_category": "meta"
        })

    return decisions
