import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from db.db_models import TeamMember, TeamMemberInteraction

# Weighted behaviour patterns
STATUS_OPTIONS = ["To Do", "In Progress", "Review", "Done", "Blocked"]
COMMENT_SNIPPETS = [
    "Pushing this forward.",
    "Added clarification to the description.",
    "Waiting on feedback.",
    "Updated acceptance criteria.",
    "Resolved merge conflict.",
    "Investigating root cause."
]

def generate_synthetic_sprint(db: Session, days: int = 10, events_per_day: int = 20):
    """
    Populate the SAAM DB with synthetic Jira-like interactions
    for all team members over a simulated sprint.
    """

    members = db.query(TeamMember).all()
    if not members:
        raise Exception("No team members found. Trigger at least one Jira event first.")

    start_date = datetime.utcnow() - timedelta(days=days)

    for day in range(days):
        for _ in range(events_per_day):
            member = random.choice(members)
            timestamp = start_date + timedelta(days=day, seconds=random.randint(0, 86400))

            signal_type, metadata = generate_random_signal()

            interaction = TeamMemberInteraction(
                team_member_id=member.id,
                signal_type=signal_type,
                weight=metadata.get("weight", 1.0),
                metadata=metadata,
                created_at=timestamp
            )

            db.add(interaction)

    db.commit()
    return {
        "status": "ok",
        "message": f"Generated synthetic sprint: {days} days, {events_per_day} events/day"
    }


def generate_random_signal():
    """
    Randomly generate a realistic Jira behavioural signal.
    """

    roll = random.random()

    # 20% comments
    if roll < 0.20:
        return "comment_created", {
            "weight": 1.0,
            "body": random.choice(COMMENT_SNIPPETS)
        }

    # 25% status transitions
    if roll < 0.45:
        from_status = random.choice(STATUS_OPTIONS)
        to_status = random.choice([s for s in STATUS_OPTIONS if s != from_status])
        weight = 2.0 if to_status == "Blocked" else 1.0
        return "status_transition", {
            "weight": weight,
            "from": from_status,
            "to": to_status
        }

    # 20% assignments
    if roll < 0.65:
        return "assignment_changed", {
            "weight": 1.2,
            "from": None,
            "to": "User"
        }

    # 35% field edits
    return "field_edited", {
        "weight": 0.5,
        "field": "Rank",
        "from": "Medium",
        "to": "High"
    }
