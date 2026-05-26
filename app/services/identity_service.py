from sqlalchemy.orm import Session
from db.db_models import TeamMember, TeamMemberExternalIdentity


def resolve_identity(
    db: Session,
    source: str,
    external_id: str,
    display_name: str,
    email: str | None = None
):
    """
    Universal identity resolver for Jira, Teams, Git, Slack, etc.
    Ensures:
    - stable internal TeamMember identity
    - up‑to‑date display name + email
    - consistent external identity mapping
    """

    # --- 1. Look for an existing external identity mapping ------------------
    mapping = (
        db.query(TeamMemberExternalIdentity)
        .filter_by(source=source, external_id=external_id)
        .first()
    )

    if mapping:
        member = mapping.team_member
        updated = False

        # Update display name if changed
        if member.display_name != display_name:
            member.display_name = display_name
            updated = True

        # Update email if provided and changed
        if email and member.email != email:
            member.email = email
            updated = True

        if updated:
            db.commit()
            db.refresh(member)

        return member

    # --- 2. No mapping → create a new TeamMember ----------------------------
    member = TeamMember(
        display_name=display_name,
        email=email,
        active=True,
    )
    db.add(member)
    db.commit()
    db.refresh(member)

    # --- 3. Create the external identity mapping ----------------------------
    new_mapping = TeamMemberExternalIdentity(
        team_member_id=str(member.id),
        source=source,
        external_id=external_id,
    )
    db.add(new_mapping)
    db.commit()

    return member
