from sqlalchemy.orm import Session
from db.db_models import (
    JiraUser, JiraIssue, JiraEvent,
    TeamMember, TeamMemberExternalIdentity,
    TeamMemberInteraction
)
from app.engine.signals import extract_signals_from_event
import uuid
from datetime import datetime

def process_jira_issue(db: Session, payload: dict):
    """
    Shared ingestion logic for both webhooks and JSON imports.
    """
    # 1. Extract core fields
    issue_key = payload.get("issue", {}).get("key")
    user_info = payload.get("user", {})
    event_type = payload.get("webhookEvent")

    # 2. Resolve JiraUser → TeamMember
    account_id = user_info.get("accountId")
    display_name = user_info.get("displayName")
    email = user_info.get("emailAddress")

    jira_user = db.query(JiraUser).filter_by(account_id=account_id).first()
    if not jira_user:
        jira_user = JiraUser(
            id=str(uuid.uuid4()),
            account_id=account_id,
            display_name=display_name,
            email=email
        )
        db.add(jira_user)
        db.commit()

    if not jira_user.team_member_id:
        tm = db.query(TeamMember).filter_by(email=email).first()
        if not tm:
            tm = TeamMember(
                id=str(uuid.uuid4()),
                display_name=display_name,
                email=email
            )
            db.add(tm)
            db.commit()

        ext = TeamMemberExternalIdentity(
            id=str(uuid.uuid4()),
            team_member_id=tm.id,
            source="jira",
            external_id=account_id
        )
        db.add(ext)
        db.commit()

        jira_user.team_member_id = tm.id
        db.commit()

    # 3. Upsert JiraIssue
    issue = db.query(JiraIssue).filter_by(issue_key=issue_key).first()
    if not issue:
        issue = JiraIssue(
            id=str(uuid.uuid4()),
            issue_key=issue_key
        )
        db.add(issue)

    fields = payload["issue"]["fields"]
    issue.summary = fields.get("summary")
    issue.status = fields["status"]["name"]
    issue.issue_type = fields["issuetype"]["name"]
    issue.priority = fields["priority"]["name"]
    issue.updated_at = datetime.utcnow()

    db.commit()

    # 4. Create JiraEvent
    event = JiraEvent(
        id=str(uuid.uuid4()),
        issue_id=issue.id,
        event_type=event_type,
        raw_payload=payload,
        triggered_by_id=jira_user.id,
        timestamp=datetime.utcnow()
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # 5. Extract behavioural signals
    signals = extract_signals_from_event(event_type, payload)

    for sig in signals:
        interaction = TeamMemberInteraction(
            id=str(uuid.uuid4()),
            team_member_id=jira_user.team_member_id,
            jira_event_id=event.id,
            signal_type=sig["type"],
            weight=sig["weight"],
            event_metadata=sig.get("metadata"),
            timestamp=datetime.utcnow()
        )
        db.add(interaction)

    db.commit()
