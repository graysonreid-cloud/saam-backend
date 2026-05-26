from typing import Dict


def _normalise_by_max(values: Dict[str, float]) -> Dict[str, float]:
    """
    Normalise values to a 0–1 range by dividing by the maximum.
    Avoids division by zero by falling back to 1.0.
    """
    if not values:
        return {}
    max_val = max(values.values()) or 1.0
    return {k: v / max_val for k, v in values.items()}


def normalise_member_participation(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Participation = actions + responses.
    Higher activity → higher participation score.
    """
    raw = {
        member: m.get("actions", 0.0) + m.get("responses", 0.0)
        for member, m in member_metrics.items()
    }
    return _normalise_by_max(raw)


def normalise_member_blockers(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Blocker severity = average blocker age.
    Older blockers → higher severity score.
    """
    raw = {
        member: m.get("avg_blocker_age", 0.0)
        for member, m in member_metrics.items()
    }
    return _normalise_by_max(raw)


def normalise_member_interaction(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Interaction load = how much attention a member requires.
    Higher load → higher normalised score.
    """
    raw = {
        member: m.get("interaction_load", 0.0)
        for member, m in member_metrics.items()
    }
    return _normalise_by_max(raw)
