from app.engine.trace_builder import build_trace

def build_decision_summary(decisions, best, team_state, confidence=None, team_health=None, **extra):
    """
    Build a structured, explainable summary of SAAM's reasoning.
    This is the core MVP output for the thesis.
    """

    # Sort all decisions by priority (highest first)
    ordered = sorted(decisions, key=lambda d: d["priority"], reverse=True)

    # Extract structured fields
    cues = [d["cue"] for d in ordered]
    rule_names = [d["rule_name"] for d in ordered]
    explanations = [d["explanation"] for d in ordered]
    priorities = [d["priority"] for d in ordered]

    # Build explainability trace
    trace = build_trace(ordered, team_state)

    return {
        "final_decision": best,
        "all_decisions": ordered,
        "decision_count": len(decisions),
        "highest_priority": best["priority"] if best else None,

        # Structured reasoning fields
        "cues_triggered": cues,
        "rule_names": rule_names,
        "explanations": explanations,
        "priorities": priorities,

        # Explainability trace
        "trace": trace,
        "confidence": confidence,
 
        # Echo team state for transparency
        "team_state": team_state
    }
