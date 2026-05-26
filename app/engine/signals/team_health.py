def calculate_team_health(state: dict) -> int:
    """
    Produces a 0–100 team health score for the standup.
    Higher = healthier.
    """

    participation = state.get("participation", 0)  # already 0–1
    imbalance = state.get("talk_time_imbalance", 0)  # 0–1
    blocker_age = state.get("blocker_age_days", 0)
    missing_updates = state.get("missing_updates", False)

    # 1. Participation (weight: 35%)
    participation_score = participation

    # 2. Talk-time balance (weight: 25%)
    imbalance_score = 1 - min(imbalance, 1)

    # 3. Blocker severity (weight: 30%)
    if blocker_age == 0:
        blocker_score = 1
    elif blocker_age <= 2:
        blocker_score = 0.7
    elif blocker_age <= 5:
        blocker_score = 0.4
    else:
        blocker_score = 0.1

    # 4. Reporting completeness (weight: 10%)
    reporting_score = 0 if missing_updates else 1

    # Weighted health score
    health = (
        0.35 * participation_score +
        0.25 * imbalance_score +
        0.30 * blocker_score +
        0.10 * reporting_score
    )

    return int(round(health * 100))
