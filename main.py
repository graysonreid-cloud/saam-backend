from fastapi import FastAPI
from pydantic import BaseModel
from app.engine.evaluator import evaluate_team_state

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
