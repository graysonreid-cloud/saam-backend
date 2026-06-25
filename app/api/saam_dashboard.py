from fastapi import APIRouter, Depends
from datetime import datetime
from db.database import get_db
from app.services.saam_output import build_saam_output

router = APIRouter()

@router.get("/saam/dashboard")
def saam_dashboard(db=Depends(get_db)):
    """
    Returns a structured dashboard-style summary of SAAM output.
    Includes:
      - per-user behavioural stats
      - collaboration score
      - perceptron label
      - last updated timestamp
    """
    data = build_saam_output(db)

    dashboard = {
        "last_updated": datetime.utcnow().isoformat() + "Z",
        "team_size": len(data),
        "healthy_count": sum(1 for m in data if m["saam_label"] == "healthy"),
        "low_collaboration_count": sum(1 for m in data if m["saam_label"] == "low_collaboration"),
        "members": data
    }

    return dashboard
