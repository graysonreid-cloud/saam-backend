from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from db.db_models import TeamMemberInteraction
from app.services.synthetic_sprint import generate_synthetic_sprint
from db.database import SessionLocal

# Load environment variables early
load_dotenv()


app = FastAPI(title="SAAM Backend")

from app.api.webhooks.jira_webhook import router as jira_router
app.include_router(jira_router, prefix="/webhook")

from app.integrations.jira_client import fetch_jira_issue
from app.engine.evaluator import evaluate_team_state

from app.api.ingest.json_ingest import router as json_ingest_router
app.include_router(json_ingest_router)

from app.api.saam_output import router as saam_output_router
app.include_router(saam_output_router)

from app.api.saam_dashboard import router as saam_dashboard_router
app.include_router(saam_dashboard_router)

from app.api.model_inspection import router as model_inspection_router
app.include_router(model_inspection_router)

from app.api.training_template import router as training_template_router
app.include_router(training_template_router)

from app.api.team_summary import router as team_summary_router
app.include_router(team_summary_router, prefix="/api")

from app.api.risk_trend import router as risk_trend_router
app.include_router(risk_trend_router, prefix="/api")

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


@app.on_event("startup")
def populate_if_empty():
    db = SessionLocal()
    count = db.query(TeamMemberInteraction).count()

    if count == 0:
        print("SAAM: Empty DB detected — generating synthetic sprint...")
        generate_synthetic_sprint(db)
    else:
        print("SAAM: Existing data detected — skipping synthetic sprint.")

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
        jira_data = fetch_jira_issue(issue_key)

    state = payload.get("state", {})
    state["jira"] = jira_data

    return evaluate_team_state(state)