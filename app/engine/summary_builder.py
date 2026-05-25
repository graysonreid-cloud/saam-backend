def build_decision_summary(best, decisions, state, confidence, team_health, trace):
    """
    Summary Builder:
    Produces a clean, structured summary used by Teams, logs, and thesis screenshots.
    """

    return {
        "final_decision": best,
        "all_decisions": decisions,
        "normalised_signals": {
            "participation_norm": state.get("participation_norm"),
            "imbalance_norm": state.get("imbalance_norm"),
            "blocker_age_norm": state.get("blocker_age_norm"),
            "time_remaining_norm": state.get("time_remaining_norm"),
            "missing_updates_norm": state.get("missing_updates_norm"),
        },
        "confidence": confidence,
        "team_health": team_health,
        "trace": trace,
        "standup_reasoning": best.get("standup_reasoning"),
    }
