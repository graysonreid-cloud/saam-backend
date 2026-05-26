from fastapi import FastAPI, Request, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# ---------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------
app = FastAPI(title="SAAM Backend")

# ---------------------------------------------------------
# Routers & Integrations
# ---------------------------------------------------------
from app.integrations.jira_client import fetch_jira_issue
from app.integrations.jira.mapping import map_jira_to_saam
from app.engine.evaluator import evaluate_team_state

# Jira webhook router
from app.api.webhooks.jira_webhook import router as jira_router

# Register routers
app.include_router(jira_router)

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------
class TeamState(BaseModel):
    participation: float
    talk_time_imbalance: float
    blocker_age_days: int
    blocker_owner_missing: bool
    ceremony: str
    time_remaining: int

# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# ---------------------------------------------------------
# Manual Evaluation Endpoint
# ---------------------------------------------------------
@app.post("/evaluate")
def evaluate(state: TeamState):
    return evaluate_team_state(state)

# ---------------------------------------------------------
# Evaluate with Jira (manual fetch)
# ---------------------------------------------------------
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
            api_token=jira_config.get("api_token"),
        )

    state = payload.get("state", {})
    state["jira"] = jira_data

    return evaluate_team_state(state)

# ---------------------------------------------------------
# Legacy Jira Webhook (kept for compatibility)
# ---------------------------------------------------------
@app.post("/webhooks/jira")
async def jira_webhook(payload: dict):
    print("Webhook payload received:", payload)

    issue = payload.get("issue")
    if not issue:
        return {"error": "Missing issue"}

    try:
        saam_state = map_jira_to_saam(issue)
        print("Mapped SAAM state:", saam_state)

        decision = evaluate_team_state(saam_state)
        print("SAAM decision:", decision)

        return {
            "status": "ok",
            "saam_state": saam_state,
            "decision": decision,
        }

    except Exception as e:
        print("WEBHOOK ERROR:", e)
        return {"error": str(e)}
