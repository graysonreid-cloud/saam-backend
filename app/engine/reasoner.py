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
