from fastapi import APIRouter, Depends
from db.database import get_db
from app.services.member_aggregation import aggregate_member_interactions
from app.saam.cues import extract_cues
from app.saam.features import FEATURE_ORDER

router = APIRouter()

@router.get("/saam/training-template")
def training_template(db=Depends(get_db)):
    """
    Generates a training dataset template using full SAAM cues.
    Labels are set to None so they can be manually assigned.
    """

    members = aggregate_member_interactions(db)

    template = []

    for m in members:
        # Convert aggregated stats → SAAM cues (includes risk_score)
        cues = extract_cues(m)

        # Build row in feature order
        feature_row = {feature: cues.get(feature) for feature in FEATURE_ORDER}

        template.append({
            "user_id": m["user_id"],
            "display_name": m["display_name"],
            "features": feature_row,
            "risk_score": cues.get("risk_score"),
            "label": None  # 0=silent, 1=healthy, 2=blocked
        })

    return {
        "count": len(template),
        "instructions": (
            "Fill in 'label' for each user: "
            "0 = silent, 1 = healthy, 2 = blocked. "
            "Then POST the completed dataset to /saam/train."
        ),
        "feature_order": FEATURE_ORDER,
        "data": template
    }
