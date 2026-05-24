import json
from app.engine.rules import apply_rules
from app.engine.prioritizer import choose_best_intervention
from app.engine.reasoner import build_reasoning_trace
from app.engine.teams_formatter import build_teams_message
from app.saam_logger.logger import log_intervention
from app.engine.trace_builder import build_trace
from app.engine.confidence import calculate_confidence
from app.engine.reasoner import build_standup_reasoning
from app.engine.team_health import calculate_team_health


def evaluate_team_state(state):

    # Convert Pydantic model to dict if needed
    if hasattr(state, "dict"):
        state = state.dict()

    # Run rules → get all candidate decisions
    candidates = apply_rules(state)

    # Pick the best intervention
    best = choose_best_intervention(candidates)

    # Add Jira summary/status if present
    jira_data = state.get("jira")
    if jira_data and "error" not in jira_data:
        state["jira_summary"] = jira_data.get("fields", {}).get("summary")
        state["jira_status"] = jira_data.get("fields", {}).get("status", {}).get("name")

    # Build reasoning trace for the best decision
    reasoning_trace = build_reasoning_trace(candidates, best)
    best["reasoning_trace"] = reasoning_trace

    # Calculate confidence FIRST
    confidence = calculate_confidence(candidates, best)
    best["confidence"] = confidence

    # Build standup reasoning
    standup_reasoning = build_standup_reasoning(candidates, best)
    best["standup_reasoning"] = standup_reasoning

    # Calculate team health
    team_health = calculate_team_health(state)
    best["team_health"] = team_health

    # Build Teams message LAST so it includes confidence + health
    best["teams_message"] = build_teams_message(best)

    # Log raw JSON for audit/debugging
    raw_json = json.dumps(best, ensure_ascii=False)
    log_intervention(best, raw_json)

    # Return full explainability summary
    return build_decision_summary(candidates, best, state)


def build_decision_summary(decisions, best, team_state):
    ordered = sorted(decisions, key=lambda d: d["priority"], reverse=True)

    return {
        "final_decision": best,
        "all_decisions": ordered,
        "decision_count": len(decisions),
        "highest_priority": best["priority"] if best else None,
        "cues_triggered": [d["cue"] for d in ordered],
        "rule_names": [d["rule_name"] for d in ordered],
        "team_state": team_state,
        "confidence": best.get("confidence"),
        "reasoning": best.get("reasoning"),
        "team_health": best.get("team_health"),
        "trace": build_trace(ordered, team_state)
    }
