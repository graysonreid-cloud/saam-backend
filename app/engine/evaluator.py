import json
import uuid

from app.engine.rules.core_rules import apply_rules
from app.engine.prioritizer import choose_best_intervention
from app.engine.summary.teams_formatter import build_teams_message
from app.engine.summary.trace_builder import build_trace
from app.engine.summary.summary_builder import build_decision_summary
from app.engine.reasoner import build_standup_reasoning
from app.engine.signals.confidence import calculate_confidence
from app.engine.signals.team_health import calculate_team_health
from app.engine.signals.normalisation import normalise_state
from app.engine.rules.standup_rules import standup_rules
from app.engine.members.member_rules import member_rules
from app.engine.members.member_metrics import compute_member_metrics
from app.engine.signals.member_normalisation import (
    normalise_member_participation,
    normalise_member_blockers,
    normalise_member_interaction,
)

from app.saam_logger.logger import log_intervention
from db.database import SessionLocal
from db.db_models import MemberBehaviour
from db.db_utils import resolve_team_member_id


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

    # Team‑level normalisation
    state = normalise_state(state)

    # Member‑level metrics
    events = state.get("events") or []
    if events:
        metrics = compute_member_metrics(events)
        state.update({
            "member_metrics": metrics,
            "member_participation_norm": normalise_member_participation(metrics),
            "member_blocker_norm": normalise_member_blockers(metrics),
            "member_interaction_norm": normalise_member_interaction(metrics),
        })
    else:
        state.update({
            "member_metrics": {},
            "member_participation_norm": {},
            "member_blocker_norm": {},
            "member_interaction_norm": {},
        })

    # Rule engines
    candidates = (
        apply_rules(state)
        + member_rules(state)
        + (standup_rules(state) if state.get("ceremony") == "standup" else [])
    )

    if not candidates:
        return _empty_summary(state)

    # Best intervention
    best = choose_best_intervention(candidates)

    # Confidence, reasoning, health, Teams message
    best["confidence"] = calculate_confidence(candidates, best, state)
    best["standup_reasoning"] = build_standup_reasoning(candidates, best)
    best["team_health"] = calculate_team_health(state)
    best["teams_message"] = build_teams_message(best)

    # Logging
    log_intervention(best, json.dumps(best, ensure_ascii=False))

    # Trace + summary
    trace = build_trace(candidates, state)
    summary = build_decision_summary(
        decisions=candidates,
        best=best,
        team_state=state,
        confidence=best["confidence"],
        team_health=best["team_health"],
        teams_message=best["teams_message"],
        standup_reasoning=best["standup_reasoning"],
        trace=trace,
    )

    # Persist member behaviour
    _save_member_behaviour(state, candidates)

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


def _save_member_behaviour(state, candidates):
    """Persist per‑member behavioural metrics."""
    try:
        db = SessionLocal()

        metrics = state.get("member_metrics", {})
        part = state.get("member_participation_norm", {})
        block = state.get("member_blocker_norm", {})
        inter = state.get("member_interaction_norm", {})

        triggered = {}
        for d in candidates:
            member = d.get("member")
            if member:
                triggered.setdefault(member, []).append(d["rule_name"])

        for member_name, m in metrics.items():
            team_member_id = resolve_team_member_id(db, member_name)

            record = MemberBehaviour(
                request_id=state.get("request_id"),
                team_member_id=team_member_id,
                actions=m.get("actions", 0),
                responses=m.get("responses", 0),
                issues=m.get("issues", 0),
                avg_blocker_age=m.get("avg_blocker_age", 0.0),
                interaction_load=m.get("interaction_load", 0.0),
                participation_norm=part.get(member_name, 0.0),
                blocker_norm=block.get(member_name, 0.0),
                interaction_norm=inter.get(member_name, 0.0),
                triggered_rules=triggered.get(member_name, []),
            )

            db.add(record)

        db.commit()

    except Exception as e:
        print("Error saving member behaviour:", e)
    finally:
        if "db" in locals():
            db.close()
