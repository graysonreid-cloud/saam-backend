from typing import Dict


def _normalise_by_max(values: Dict[str, float]) -> Dict[str, float]:
    if not values:
        return {}
    max_val = max(values.values()) or 1.0
    return {k: v / max_val for k, v in values.items()}


def normalise_member_participation(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Higher actions + responses → higher participation.
    """
    raw = {}
    for member, m in member_metrics.items():
        raw[member] = m.get("actions", 0.0) + m.get("responses", 0.0)
    return _normalise_by_max(raw)


def normalise_member_blockers(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Higher avg_blocker_age → higher blocker severity.
    """
    raw = {}
    for member, m in member_metrics.items():
        raw[member] = m.get("avg_blocker_age", 0.0)
    return _normalise_by_max(raw)


def normalise_member_interaction(member_metrics: Dict[str, Dict[str, float]]) -> Dict[str, float]:
    """
    Higher interaction_load → higher need for SM attention.
    """
    raw = {}
    for member, m in member_metrics.items():
        raw[member] = m.get("interaction_load", 0.0)
    return _normalise_by_max(raw)
