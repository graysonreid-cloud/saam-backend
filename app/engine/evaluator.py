import json
from app.engine.rules import apply_rules
from app.engine.prioritizer import choose_best_intervention
from app.engine.reasoner import build_reasoning_trace
from app.engine.teams_formatter import build_teams_message
from app.saam_logger.logger import log_intervention


def evaluate_team_state(state):
    candidates = apply_rules(state)
    best = choose_best_intervention(candidates)

    reasoning = build_reasoning_trace(candidates, best)
    best["reasoning_trace"] = reasoning

    best["teams_message"] = build_teams_message(best)

    raw_json = json.dumps(best, ensure_ascii=False)
    log_intervention(best, raw_json)

    return best

