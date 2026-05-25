from sqlalchemy.orm import Session
from db.db_models import TeamMember

def resolve_team_member_id(db: Session, name: str):
    """
    Resolve a team member name to a canonical TeamMember.id.
    If not found, return None (we allow anonymous members).
    """
    member = db.query(TeamMember).filter(TeamMember.display_name == name).first()
    return member.id if member else None
