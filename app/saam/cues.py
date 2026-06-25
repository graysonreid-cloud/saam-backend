# app/saam/cues.py

def extract_cues(raw: dict) -> dict:
    """
    Convert raw behavioural stats into SAAM cue values.
    This is the foundation for the trained model.
    """

    # 1. Participation level (0–1)
    participation_level = raw.get("participation_level", 0)

    # 2. Talktime imbalance (0–1)
    talktime_imbalance = raw.get("talktime_imbalance", 0)

    # 3. Blocker age (days)
    blocker_age = raw.get("blocker_age", 0)

    # 4. Missing updates (0 or 1)
    missing_updates = 1 if raw.get("missing_updates", False) else 0

    # 5. Blocker owner missing (0 or 1)
    blocker_owner_missing = 1 if raw.get("blocker_owner_missing", False) else 0

    # 6. Time remaining in sprint (days)
    time_remaining = raw.get("time_remaining", 0)

    # 7. Goal changes (count)
    goal_changes = raw.get("goal_changes", 0)

    # 8. Ceremony type (categorical → encoded)
    ceremony_map = {
        "standup": 0,
        "planning": 1,
        "retro": 2,
        "refinement": 3
    }
    ceremony_type_encoded = ceremony_map.get(raw.get("ceremony_type", "standup"), 0)

    # 9. Sentiment score (-1 to +1)
    sentiment_score = raw.get("sentiment_score", 0)

    # 10. Workload ratio (0–2)
    workload_ratio = raw.get("workload_ratio", 1)

    # 11. Help requests (count)
    help_requests = raw.get("help_requests", 0)

    # 12. Help offers (count)
    help_offers = raw.get("help_offers", 0)

    return {
        "participation_level": participation_level,
        "talktime_imbalance": talktime_imbalance,
        "blocker_age": blocker_age,
        "missing_updates": missing_updates,
        "blocker_owner_missing": blocker_owner_missing,
        "time_remaining": time_remaining,
        "goal_changes": goal_changes,
        "ceremony_type_encoded": ceremony_type_encoded,
        "sentiment_score": sentiment_score,
        "workload_ratio": workload_ratio,
        "help_requests": help_requests,
        "help_offers": help_offers
    }
