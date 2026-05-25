def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0
    return max(min_val, min(value, max_val))


def normalise_blocker_age(days) -> float:
    try:
        days = int(days)
    except (TypeError, ValueError):
        days = 0

    if days <= 0:
        return 0.0
    if days <= 2:
        return 0.3
    if days <= 5:
        return 0.6
    if days <= 10:
        return 0.8
    return 1.0


def normalise_time_remaining(minutes) -> float:
    try:
        minutes = int(minutes)
    except (TypeError, ValueError):
        minutes = 10  # safe default

    if minutes <= 0:
        return 1.0
    if minutes >= 10:
        return 0.0
    return clamp((10 - minutes) / 10)


def normalise_state(state: dict) -> dict:
    normalised = dict(state)

    normalised["participation_norm"] = clamp(state.get("participation", 0))
    normalised["imbalance_norm"] = clamp(state.get("talk_time_imbalance", 0))
    normalised["blocker_age_norm"] = normalise_blocker_age(state.get("blocker_age_days", 0))
    normalised["time_remaining_norm"] = normalise_time_remaining(state.get("time_remaining", 10))
    normalised["missing_updates_norm"] = 1.0 if state.get("missing_updates") else 0.0

    return normalised
