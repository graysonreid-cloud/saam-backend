from typing import List, Dict, Any

def build_reasoning_trace(candidates: List[Dict[str, Any]], final_choice: Dict[str, Any]) -> List[str]:
    trace = []

    # 1. Which rules fired
    trace.append("Rules triggered:")
    for c in candidates:
        trace.append(f"- [{c['rule_name']}] {c['explanation']} (priority {c['priority']})")

    # 2. If multi-cue composite
    if final_choice.get("rule_name") == "multi_cue_composite":
        trace.append("")
        trace.append("Multiple high-priority cues detected:")
        for r in final_choice["contributing_rules"]:
            trace.append(f"- {r}")

        trace.append("")
        trace.append("Composite intervention created because multiple cues exceeded the severity threshold.")

    # 3. Why this rule was chosen
    trace.append("")
    trace.append(f"Final decision: [{final_choice['rule_name']}] with priority {final_choice['priority']}.")

    # 4. Rationale
    trace.append(f"Rationale: {final_choice['rationale']}")

    return trace



def build_standup_reasoning(decisions: list, best: dict) -> dict:
    """
    Produces a deeper behavioural interpretation of the standup signals.
    """

    if not decisions or not best:
        return {
            "dominant_signal": None,
            "behavioural_pattern": "No significant signals detected.",
            "reason_for_choice": "No rules fired.",
            "risk_category": "None"
        }

    # 1. Dominant signal = highest priority cue
    dominant_signal = best.get("cue")

    # 2. Behavioural pattern detection
    cues = [d["cue"] for d in decisions]

    if "team_silence_plus_dominance" in cues:
        behavioural_pattern = (
            "Low participation combined with dominance suggests a psychological safety risk."
        )
    elif "blocker_unowned_aged" in cues or "critical_blocker" in cues:
        behavioural_pattern = (
            "A critical blocker is affecting flow and requires immediate attention."
        )
    elif "low_participation" in cues:
        behavioural_pattern = (
            "Participation is uneven, indicating reduced engagement or communication imbalance."
        )
    elif "dominant_voice" in cues:
        behavioural_pattern = (
            "One voice is dominating the standup, reducing team contribution."
        )
    else:
        behavioural_pattern = (
            "Multiple signals detected, but none indicate severe dysfunction."
        )

    # 3. Why this rule won
    highest_priority = max(d["priority"] for d in decisions)
    competing = [d for d in decisions if d["priority"] == highest_priority]

    if len(competing) > 1:
        reason_for_choice = (
            f"Multiple high‑priority signals were detected ({len(competing)}). "
            f"SAAM selected '{best['rule_name']}' as the most actionable intervention."
        )
    else:
        reason_for_choice = (
            f"The rule '{best['rule_name']}' had the highest priority "
            f"({best['priority']}), indicating the most urgent team need."
        )

    # 4. Risk category
    if best["priority"] >= 7:
        risk_category = "Critical"
    elif best["priority"] >= 5:
        risk_category = "High"
    elif best["priority"] >= 3:
        risk_category = "Moderate"
    else:
        risk_category = "Low"

    return {
        "dominant_signal": dominant_signal,
        "behavioural_pattern": behavioural_pattern,
        "reason_for_choice": reason_for_choice,
        "risk_category": risk_category
    }
