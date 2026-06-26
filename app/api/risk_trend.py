# app/api/risk_trend.py

from fastapi import APIRouter
from datetime import datetime
from app.saam.risk_trend import compute_risk_trend

router = APIRouter()

@router.get("/team/risk/trend")
def risk_trend(days: int = 14):
    trend = compute_risk_trend(days)
    return {
        "status": "ok",
        "generated_at": datetime.utcnow().isoformat(),
        "days": days,
        "trend": trend
    }
