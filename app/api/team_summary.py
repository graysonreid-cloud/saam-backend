# app/api/team_summary.py

from fastapi import APIRouter
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from db.database import SessionLocal
from app.saam.team_summary import compute_daily_team_summary

router = APIRouter()

@router.get("/team/summary/daily")
def daily_team_summary():
    db: Session = SessionLocal()
    try:
        summary = compute_daily_team_summary(db)
        return {
            "status": "ok",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary": summary
        }
    finally:
        db.close()
