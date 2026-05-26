from typing import Dict, List, Any


def member_rules(state: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate per‑member behavioural interventions based on normalised metrics.
    """

    decisions = []

    metrics = state.get("member_metrics") or {}
    part = state.get("member_participation_norm") or {}
    block = state.get("member_blocker_norm") or {}
    inter = state.get("member_interaction_norm") or {}

    for member, _ in metrics.items():
        # Extract normalised signals for this member
        p = part.get(member, 0.0)
        b = block.get(member, 0.0)
        i = inter.get(member, 0.0)

        signals = {
            "participation_norm": p,
            "blocker_norm": b,
            "interaction_norm": i,
        }

        # Declarative rule table: (condition, name, category, priority, message, explanation)
        rules = [
            (
                p < 0.3,
                "member_low_participation",
                "member_participation",
                6,
                f"{member} has low participation in recent interactions.",
                f"{member}'s participation score is low compared to others. "
                "Consider inviting them explicitly into the conversation.",
            ),
            (
                b > 0.6,
                "member_high_blocker_age",
                "member_blockers",
                7,
                f"{member} has blockers that have been open for a long time.",
                f"{member}'s average blocker age is high relative to the team. "
                "Consider focusing on unblocking their work.",
            ),
            (
                i > 0.6,
                "member_high_interaction_load",
                "member_interaction",
                7,
                f"{member} requires a high level of interaction from the Scrum Master.",
                f"{member}'s interaction load is high. "
                "Consider checking whether they need additional support or clarity.",
            ),
        ]

        # Evaluate rules for this member
        for condition, name, category, priority, message, explanation in rules:
            if condition:
                decisions.append({
                    "rule_name": name,
                    "rule_category": category,
                    "cue": f"{name.replace('_', ' ')} for {member}",
                    "priority": priority,
                    "message": message,
                    "explanation": explanation,
                    "member": member,
                    "member_signals": signals,
                })

    return decisions
