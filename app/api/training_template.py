from fastapi import APIRouter, Depends
from db.database import get_db
from app.services.member_aggregation import aggregate_member_interactions

router = APIRouter()

@router.get("/saam/training-template")
def training_template(db=Depends(get_db)):
    """
    Generates a training dataset template based on current aggregated behaviour.
    Labels are set to null so they can be manually assigned.
    """
    members = aggregate_member_interactions(db)

    template = []
    for m in members:
        template.append({
            "user_id": m["user_id"],
            "display_name": m["display_name"],
            "comments": m["comments"],
            "assignments": m["assignments"],
            "transitions": m["transitions"],
            "label": None  # to be filled manually
        })

    return {
        "count": len(template),
        "instructions": (
            "Fill in 'label' for each user: 1 = healthy, 0 = low_collaboration. "
            "Then POST the completed dataset to /saam/train."
        ),
        "data": template
    }
