from sqlalchemy.orm import Session
from db.db_models import TeamMember

def resolve_team_member_id(db: Session, name: str):
    """
    Resolve a display name to a canonical TeamMember.id.
    Returns None if no matching member exists (anonymous allowed).
    """
    member = (
        db.query(TeamMember)
        .filter(TeamMember.display_name == name)
        .first()
    )
    return member.id if member else None
