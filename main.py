from fastapi import FastAPI
from pydantic import BaseModel
from app.engine.evaluator import evaluate_team_state
from app.integrations.jira_client import fetch_jira_issue

app = FastAPI(title="SAAM Backend")

class TeamState(BaseModel):
    participation: float
    talk_time_imbalance: float
    blocker_age_days: int
    blocker_owner_missing: bool
    ceremony: str
    time_remaining: int

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/evaluate")
def evaluate(state: TeamState):
    return evaluate_team_state(state)

@app.post("/evaluate_with_jira")
def evaluate_with_jira(payload: dict):
    issue_key = payload.get("issue_key")
    jira_config = payload.get("jira", {})

    jira_data = None
    if issue_key and jira_config:
        jira_data = fetch_jira_issue(
            issue_key=issue_key,
            base_url=jira_config.get("base_url"),
            username=jira_config.get("username"),
            api_token=jira_config.get("api_token")
        )

    # Pass Jira data into SAAM state
    state = payload.get("state", {})
    state["jira"] = jira_data

    return evaluate_team_state(state)
