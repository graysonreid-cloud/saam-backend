from typing import Dict, List, Any


def member_rules(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Per-member behavioural rules based on normalised metrics.

    Expects in state:
    - member_metrics
    - member_participation_norm
    - member_blocker_norm
    - member_interaction_norm
    """

    decisions: List[Dict[str, Any]] = []

    member_metrics = state.get("member_metrics") or {}
    part_norm = state.get("member_participation_norm") or {}
    block_norm = state.get("member_blocker_norm") or {}
    inter_norm = state.get("member_interaction_norm") or {}

    for member, metrics in member_metrics.items():
        p = part_norm.get(member, 0.0)
        b = block_norm.get(member, 0.0)
        i = inter_norm.get(member, 0.0)

        # Low participation
        if p < 0.3:
            decisions.append({
                "rule_name": "member_low_participation",
                "rule_category": "member_participation",
                "cue": f"Low participation for {member}",
                "priority": 6,
                "message": f"{member} has low participation in recent interactions.",
                "explanation": (
                    f"{member}'s participation score is low compared to others. "
                    "Consider inviting them explicitly into the conversation."
                ),
                "member": member,
                "member_signals": {
                    "participation_norm": p,
                    "blocker_norm": b,
                    "interaction_norm": i,
                },
            })

        # High blocker age
        if b > 0.6:
            decisions.append({
                "rule_name": "member_high_blocker_age",
                "rule_category": "member_blockers",
                "cue": f"High blocker age for {member}",
                "priority": 7,
                "message": f"{member} has blockers that have been open for a long time.",
                "explanation": (
                    f"{member}'s average blocker age is high relative to the team. "
                    "Consider focusing on unblocking their work."
                ),
                "member": member,
                "member_signals": {
                    "participation_norm": p,
                    "blocker_norm": b,
                    "interaction_norm": i,
                },
            })

        # High interaction load
        if i > 0.6:
            decisions.append({
                "rule_name": "member_high_interaction_load",
                "rule_category": "member_interaction",
                "cue": f"High interaction load for {member}",
                "priority": 7,
                "message": f"{member} requires a high level of interaction from the Scrum Master.",
                "explanation": (
                    f"{member}'s interaction load is high. "
                    "Consider checking whether they need additional support or clarity."
                ),
                "member": member,
                "member_signals": {
                    "participation_norm": p,
                    "blocker_norm": b,
                    "interaction_norm": i,
                },
            })

    return decisions
