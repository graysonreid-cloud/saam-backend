def build_trace(decisions: list[dict], state: dict) -> list[dict]:
    """
    Trace Builder v2.
    Produces a structured, step‑by‑step reasoning trace for explainability.
    Captures:
    - rule metadata
    - normalised signals
    - rule category
    - composite contributors
    - signal severity snapshot
    - evaluation order
    """

    trace = []

    # Extract normalised signals once (shared across all entries)
    normalised = {
        "participation_norm": state.get("participation_norm"),
        "imbalance_norm": state.get("imbalance_norm"),
        "blocker_age_norm": state.get("blocker_age_norm"),
        "time_remaining_norm": state.get("time_remaining_norm"),
        "missing_updates_norm": state.get("missing_updates_norm"),
    }

    for index, d in enumerate(decisions):
        entry = {
            "order": index + 1,                     # evaluation order
            "rule_name": d.get("rule_name"),
            "rule_category": d.get("rule_category"),
            "cue": d.get("cue"),
            "priority": d.get("priority"),
            "message": d.get("message"),
            "explanation": d.get("explanation"),

            # Shared normalised signals + raw state snapshot
            "normalised_signals": normalised,
            "trigger_values": state,
        }

        # Composite rule contributors (if applicable)
        if d.get("rule_name") == "multi_cue_composite":
            entry["contributing_rules"] = d.get("contributing_rules", [])

        # Signal severity snapshot (aligned with Confidence Engine v2)
        entry["signal_severity"] = max(
            1 - (state.get("participation_norm") or 0),
            state.get("imbalance_norm") or 0,
            state.get("blocker_age_norm") or 0,
            state.get("time_remaining_norm") or 0,
        )

        trace.append(entry)

    return trace
