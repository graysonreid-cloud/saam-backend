import json
import uuid

from app.engine.rules import apply_rules
from app.engine.prioritizer import choose_best_intervention
from app.engine.teams_formatter import build_teams_message
from app.engine.trace_builder import build_trace
from app.engine.confidence import calculate_confidence
from app.engine.reasoner import build_standup_reasoning
from app.engine.team_health import calculate_team_health
from app.engine.normalisation import normalise_state
from app.engine.summary_builder import build_decision_summary
from app.rules.standup_rules import standup_rules
from app.saam_logger.logger import log_intervention


from db.database import SessionLocal
from db.db_models import MemberBehaviour
from db.db_utils import resolve_team_member_id

# NEW IMPORTS FOR MULTI‑MEMBER SUPPORT
from app.engine.member_metrics import compute_member_metrics
from app.engine.member_normalisation import (
    normalise_member_participation,
    normalise_member_blockers,
    normalise_member_interaction,
)
from app.engine.member_rules import member_rules


def evaluate_team_state(state):

    # Convert Pydantic model to dict if needed
    if hasattr(state, "dict"):
        state = state.dict()

    # PAD SAFETY: If PAD sends JSON as a string, decode it
    if isinstance(state, str):
        try:
            state = json.loads(state)
        except Exception:
            pass

    # ---------------------------------------------------------
    # 0. JIRA PAYLOAD GUARD (must be FIRST)
    # ---------------------------------------------------------
    if (
        "issue" in state
        or "webhookEvent" in state
        or "issue_event_type_name" in state
    ):
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
            "trace": []
        }

    # ---------------------------------------------------------
    # 1. Ensure request_id exists
    # ---------------------------------------------------------
    if not state.get("request_id"):
        state["request_id"] = str(uuid.uuid4())

    # ---------------------------------------------------------
    # 2. NORMALISE TEAM‑LEVEL SIGNALS
    # ---------------------------------------------------------
    state = normalise_state(state)

    # ---------------------------------------------------------
    # 3. MULTI‑MEMBER METRICS + NORMALISATION
    # ---------------------------------------------------------
    events = state.get("events") or []

    if events:
        member_metrics = compute_member_metrics(events)
        state["member_metrics"] = member_metrics

        state["member_participation_norm"] = normalise_member_participation(member_metrics)
        state["member_blocker_norm"] = normalise_member_blockers(member_metrics)
        state["member_interaction_norm"] = normalise_member_interaction(member_metrics)
    else:
        state["member_metrics"] = {}
        state["member_participation_norm"] = {}
        state["member_blocker_norm"] = {}
        state["member_interaction_norm"] = {}

    # ---------------------------------------------------------
    # 4. APPLY CORE RULES + MEMBER RULES
    # ---------------------------------------------------------
    core_candidates = apply_rules(state)
    member_candidates = member_rules(state)

    # ---------------------------------------------------------
    # 4.5 APPLY CEREMONY‑SPECIFIC RULES (STANDUP)
    # ---------------------------------------------------------
    ceremony_candidates = []
    if state.get("ceremony") == "standup":
        ceremony_candidates = standup_rules(state)

    # Combine all rule outputs
    candidates = core_candidates + member_candidates + ceremony_candidates

    if not candidates:
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
            "trace": []
        }

    # ---------------------------------------------------------
    # 5. SELECT BEST INTERVENTION
    # ---------------------------------------------------------
    best = choose_best_intervention(candidates)

    # ---------------------------------------------------------
    # 6. CONFIDENCE ENGINE v2
    # ---------------------------------------------------------
    confidence = calculate_confidence(candidates, best, state)
    best["confidence"] = confidence

    # ---------------------------------------------------------
    # 7. STANDUP REASONING
    # ---------------------------------------------------------
    standup_reasoning = build_standup_reasoning(candidates, best)
    best["standup_reasoning"] = standup_reasoning

    # ---------------------------------------------------------
    # 8. TEAM HEALTH SCORE
    # ---------------------------------------------------------
    team_health = calculate_team_health(state)
    best["team_health"] = team_health

    # ---------------------------------------------------------
    # 9. TEAMS MESSAGE
    # ---------------------------------------------------------
    best["teams_message"] = build_teams_message(best)

    # ---------------------------------------------------------
    # 10. LOGGING
    # ---------------------------------------------------------
    raw_json = json.dumps(best, ensure_ascii=False)
    log_intervention(best, raw_json)

    # ---------------------------------------------------------
    # 11. TRACE BUILDER v2
    # ---------------------------------------------------------
    trace = build_trace(candidates, state)

    # ---------------------------------------------------------
    # 12. SUMMARY BUILDER v2 (FINAL, CLEAN)
    # ---------------------------------------------------------
    summary = build_decision_summary(
        decisions=candidates,
        best=best,
        team_state=state,
        confidence=confidence,
        team_health=team_health,
        teams_message=best.get("teams_message"),
        standup_reasoning=standup_reasoning,
        trace=trace
    )

    # ---------------------------------------------------------
    # 13. PERSIST MEMBER BEHAVIOUR TO DB
    # ---------------------------------------------------------
    try:
        db = SessionLocal()

        member_metrics = state.get("member_metrics", {})
        part_norm = state.get("member_participation_norm", {})
        block_norm = state.get("member_blocker_norm", {})
        inter_norm = state.get("member_interaction_norm", {})

        triggered_by_member = {}
        for d in candidates:
            member = d.get("member")
            if member:
                triggered_by_member.setdefault(member, []).append(d["rule_name"])

        for member_name, metrics in member_metrics.items():

            team_member_id = resolve_team_member_id(db, member_name)

            record = MemberBehaviour(
                request_id=state.get("request_id"),
                team_member_id=team_member_id,
                actions=metrics.get("actions", 0),
                responses=metrics.get("responses", 0),
                issues=metrics.get("issues", 0),
                avg_blocker_age=metrics.get("avg_blocker_age", 0.0),
                interaction_load=metrics.get("interaction_load", 0.0),
                participation_norm=part_norm.get(member_name, 0.0),
                blocker_norm=block_norm.get(member_name, 0.0),
                interaction_norm=inter_norm.get(member_name, 0.0),
                triggered_rules=triggered_by_member.get(member_name, []),
            )

            db.add(record)

        db.commit()

    except Exception as e:
        print("Error saving member behaviour:", e)
    finally:
        if "db" in locals():
            db.close()

    return summary
