from typing import List, Dict, Any

def choose_best_intervention(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not candidates:
        return {
            "rule_name": "no_issue",
            "rule_category": "none",
            "rule_version": "1.0",
            "rationale": "No rules fired; team state appears healthy.",
            "cue": "no_issue",
            "message": "No intervention needed.",
            "explanation": "All monitored metrics are within healthy thresholds.",
            "priority": 0,
            "contributing_rules": [],
            "reasoning_trace": []
        }

    # Sort by priority (highest first)
    sorted_candidates = sorted(candidates, key=lambda x: x["priority"], reverse=True)

    # Take all cues above a threshold (e.g. priority >= 4)
    HIGH_PRIORITY_THRESHOLD = 4
    high_priority = [c for c in sorted_candidates if c["priority"] >= HIGH_PRIORITY_THRESHOLD]

    # If only one high‑priority cue, just return it
    if len(high_priority) <= 1:
        best = sorted_candidates[0]
        best["contributing_rules"] = [best["rule_name"]]
        return best

    # Multi‑cue composite intervention
    combined_priority = max(c["priority"] for c in high_priority)

    combined_message = "Multiple issues detected:\n" + "\n".join(
        f"- {c['message']}" for c in high_priority
    )

    combined_explanation = "This intervention combines several high‑priority signals:\n" + "\n".join(
        f"- [{c['rule_name']}] {c['explanation']}" for c in high_priority
    )

    return {
        "rule_name": "multi_cue_composite",
        "rule_category": "combined_signals",
        "rule_version": "1.0",
        "rationale": "When several high-priority cues fire together, SAAM surfaces a composite intervention.",
        "cue": "multi_cue",
        "message": combined_message,
        "explanation": combined_explanation,
        "priority": combined_priority,
        "contributing_rules": [c["rule_name"] for c in high_priority],
        "reasoning_trace": []
    }

