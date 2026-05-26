from typing import List, Dict, Any

HIGH_PRIORITY_THRESHOLD = 4


def choose_best_intervention(candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not candidates:
        return {
            "rule_name": "no_issue",
            "rule_category": "none",
            "rationale": "No rules fired; team state appears healthy.",
            "cue": "no_issue",
            "message": "No intervention needed.",
            "explanation": "All monitored metrics are within healthy thresholds.",
            "priority": 0,
            "contributing_rules": [],
            "reasoning_trace": []
        }

    # Sort by priority (highest first)
    sorted_candidates = sorted(candidates, key=lambda c: c["priority"], reverse=True)

    # High‑priority cues
    high = [c for c in sorted_candidates if c["priority"] >= HIGH_PRIORITY_THRESHOLD]

    # Single high‑priority cue → return directly
    if len(high) <= 1:
        best = sorted_candidates[0]
        best["contributing_rules"] = [best["rule_name"]]
        return best

    # Multi‑cue composite
    return {
        "rule_name": "multi_cue_composite",
        "rule_category": "combined_signals",
        "rationale": "When several high-priority cues fire together, SAAM surfaces a composite intervention.",
        "cue": "multi_cue",
        "priority": max(c["priority"] for c in high),
        "message": "Multiple issues detected:\n" + "\n".join(f"- {c['message']}" for c in high),
        "explanation": "This intervention combines several high‑priority signals:\n"
                       + "\n".join(f"- [{c['rule_name']}] {c['explanation']}" for c in high),
        "contributing_rules": [c["rule_name"] for c in high],
        "reasoning_trace": []
    }
