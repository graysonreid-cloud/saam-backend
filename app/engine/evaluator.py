import json
import uuid

from app.engine.rules.core_rules import apply_rules
from app.engine.prioritizer import choose_best_intervention
from app.engine.summary.teams_formatter import build_teams_message
from app.engine.summary.trace_builder import build_trace
from app.engine.summary.summary_builder import build_decision_summary
from app.engine.reasoner import build_standup_reasoning

def evaluate_team_state(state):
    # Accept Pydantic or JSON string
    if hasattr(state, "dict"):
        state = state.dict()
    if isinstance(state, str):
        try:
            state = json.loads(state)
        except Exception:
            pass

    # JIRA guard — short‑circuit immediately
    if any(k in state for k in ("issue", "webhookEvent", "issue_event_type_name")):
        return _empty_summary(state)

    # Ensure request_id
    state.setdefault("request_id", str(uuid.uuid4()))

    # Rule engines
    candidates = (
        apply_rules(state)
        + ([])
    )

    if not candidates:
        return _empty_summary(state)

    # Best intervention
    best = choose_best_intervention(candidates)

    # Reasoning + Teams message
    best["standup_reasoning"] = build_standup_reasoning(candidates, best)
    best["teams_message"] = build_teams_message(best)

    # Trace + summary
    trace = build_trace(candidates, state)
    summary = build_decision_summary(
        decisions=candidates,
        best=best,
        team_state=state,
        confidence=None,
        team_health=None,
        teams_message=best["teams_message"],
        standup_reasoning=best["standup_reasoning"],
        trace=trace,
    )

    return summary


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def _empty_summary(state):
    """Return a consistent empty summary structure."""
    return {
        "request_id": state.get("request_id"),
        "final_decision": None,
        "all_decisions": [],
        "decision_count": 0,
        "highest_priority": None,
        "cues_triggered": [],
        "rule_names": [],
        "team_state": state,
        "confidence": None,
        "standup_reasoning": None,
        "team_health": None,
        "trace": [],
    }
