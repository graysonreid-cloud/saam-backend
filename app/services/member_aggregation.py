from sqlalchemy.orm import Session
from db.db_models import TeamMemberInteraction, TeamMember

def aggregate_member_interactions(db: Session):
    """
    SAAM: Aggregate behavioural interactions per team member.
    Produces raw feature counts for the collaboration score + perceptron.
    """

    rows = db.query(
        TeamMemberInteraction.team_member_id,
        TeamMemberInteraction.signal_type
    ).all()

    summary = {}

    for member_id, signal in rows:
        if member_id not in summary:
            summary[member_id] = {
                "comments": 0,
                "assignments": 0,
                "transitions": 0,
            }

        # Align with REAL signal types produced by your webhook
        if signal == "comment_created":
            summary[member_id]["comments"] += 1

        elif signal == "field_edited":
            summary[member_id]["assignments"] += 1

        elif signal == "status_transition":
            summary[member_id]["transitions"] += 1

    # Attach display names for output readability
    members = db.query(TeamMember).all()
    id_to_name = {m.id: m.display_name for m in members}

    result = []
    for member_id, stats in summary.items():
        result.append({
            "user_id": member_id,
            "display_name": id_to_name.get(member_id, "Unknown"),
            **stats
        })

    return result
