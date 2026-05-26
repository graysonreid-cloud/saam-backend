from collections import defaultdict
from typing import List, Dict, Any


def compute_member_metrics(events: List[Dict[str, Any]]) -> Dict[str, Dict[str, float]]:
    members = defaultdict(lambda: {
        "actions": 0,
        "responses": 0,
        "issues": set(),
        "blocker_ages": [],
        "agent_interactions": 0,
    })

    for e in events:
        member = e.get("team_member")
        if not member:
            continue

        m = members[member]
        m["actions"] += 1

        if e.get("event_type") in {"commented", "updated", "transitioned"}:
            m["responses"] += 1

        issue = e.get("issue_key")
        if issue:
            m["issues"].add(issue)

        if (age := e.get("blocker_age_days")) is not None:
            m["blocker_ages"].append(float(age))

        if e.get("is_agent_request"):
            m["agent_interactions"] += 1

    result = {}
    for member, data in members.items():
        issues_count = len(data["issues"]) or 1
        avg_blocker_age = (
            sum(data["blocker_ages"]) / len(data["blocker_ages"])
            if data["blocker_ages"]
            else 0.0
        )

        interaction_load = (
            (data["agent_interactions"] / issues_count) * 0.6 +
            (data["actions"] / issues_count) * 0.4
        )

        result[member] = {
            "actions": float(data["actions"]),
            "responses": float(data["responses"]),
            "issues": float(issues_count),
            "avg_blocker_age": float(avg_blocker_age),
            "interaction_load": float(interaction_load),
        }

    return result
