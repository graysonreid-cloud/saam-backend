from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from app.services.saam_output import build_saam_output

router = APIRouter()

@router.get("/saam/output")
def saam_output(db: Session = Depends(get_db)):
    """
    Returns the full SAAM output:
      - Aggregated Jira behaviour
      - Collaboration score
      - Perceptron classification
    """
    data = build_saam_output(db)

    return {
        "status": "ok",
        "count": len(data),
        "data": data
    }
