from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Any


def compute_member_metrics(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    """
    Compute per-member metrics from a list of event dicts.

    Expected event fields (where available):
    - team_member: str
    - issue_key: str
    - event_type: str  (e.g., "created", "updated", "commented", "transitioned")
    - blocker_age_days: float (if applicable)
    - is_agent_request: bool (if SAAM created the request)
    """

    members: Dict[str, Dict[str, Any]] = defaultdict(
        lambda: {
            "actions": 0,
            "responses": 0,
            "issues": set(),
            "blocker_ages": [],
            "agent_interactions": 0,
        }
    )

    for e in events:
        member = e.get("team_member")
        if not member:
            continue

        m = members[member]

        # Count actions
        m["actions"] += 1

        # Responses (comments/updates)
        if e.get("event_type") in {"commented", "updated", "transitioned"}:
            m["responses"] += 1

        # Issues
        issue_key = e.get("issue_key")
        if issue_key:
            m["issues"].add(issue_key)

        # Blocker age
        blocker_age = e.get("blocker_age_days")
        if blocker_age is not None:
            m["blocker_ages"].append(float(blocker_age))

        # Agent-created interaction load
        if e.get("is_agent_request"):
            m["agent_interactions"] += 1

    # Finalise aggregates
    result: Dict[str, Dict[str, float]] = {}
    for member, data in members.items():
        issues_count = len(data["issues"]) or 1  # avoid div by zero
        avg_blocker_age = (
            sum(data["blocker_ages"]) / len(data["blocker_ages"])
            if data["blocker_ages"]
            else 0.0
        )

        # Simple interaction load heuristic:
        # agent_interactions per issue, scaled by actions
        interaction_load = (
            (data["agent_interactions"] / issues_count) * 0.6
            + (data["actions"] / max(issues_count, 1)) * 0.4
        )

        result[member] = {
            "actions": float(data["actions"]),
            "responses": float(data["responses"]),
            "issues": float(issues_count),
            "avg_blocker_age": float(avg_blocker_age),
            "interaction_load": float(interaction_load),
        }

    return result
