def build_trace(decisions: list[dict], team_state: dict) -> list[dict]:
    trace = []

    for d in decisions:
        trace.append({
            "rule_name": d["rule_name"],
            "cue": d["cue"],
            "priority": d["priority"],
            "message": d["message"],
            "explanation": d["explanation"],
            "trigger_values": team_state
        })

    return trace
