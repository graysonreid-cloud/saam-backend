from fastapi import APIRouter, Request
from sqlalchemy.orm import Session

from db.database import SessionLocal
from db.db_models import (
    Request as SAAMRequest,
    JiraUser, JiraIssue, JiraEvent,
    TeamMember, TeamMemberExternalIdentity,
    TeamMemberInteraction
)

from app.integrations.jira_client import (
    fetch_jira_issue,
    fetch_jira_user
)

from app.engine.evaluator import evaluate_team_state
from app.engine.signals import extract_signals_from_event

import uuid
from datetime import datetime

router = APIRouter()


# ---------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------

@router.post("/jira")
async def jira_webhook(request: Request):
    db: Session = SessionLocal()

    try:
        payload = await request.json()

        # -----------------------------------------------------
        # 1. Log raw request
        # -----------------------------------------------------
        req = SAAMRequest(
            id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            source="jira",
            payload=payload
        )
        db.add(req)
        db.commit()
        db.refresh(req)

        # -----------------------------------------------------
        # 2. Extract core fields
        # -----------------------------------------------------
        issue_key = payload.get("issue", {}).get("key")
        event_type = payload.get("webhookEvent")

        # -----------------------------------------------------
        # 3. Determine behavioural subject: ASSIGNEE first
        # -----------------------------------------------------
        issue_fields = payload.get("issue", {}).get("fields", {})
        assignee = issue_fields.get("assignee")

        if assignee:
            print("Assignee detected:")
            print("  displayName:", assignee.get("displayName"))
        else:
            actor = payload.get("user", {})
            print("No assignee — using actor:")
            print("  displayName:", actor.get("displayName"))


        if assignee:
            # Behaviour belongs to the assignee
            account_id = assignee.get("accountId")
            display_name = assignee.get("displayName")
            email = assignee.get("emailAddress")
        else:
            # Fallback: use actor if issue is unassigned
            actor = payload.get("user", {})
            account_id = actor.get("accountId")
            display_name = actor.get("displayName")
            email = actor.get("emailAddress")

        # -----------------------------------------------------
        # 4. Resolve JiraUser → TeamMember (accountId-based)
        # -----------------------------------------------------
        jira_user = db.query(JiraUser).filter_by(account_id=account_id).first()

        if jira_user is None:
            # Create a new TeamMember if needed
            team_member = db.query(TeamMember).filter_by(display_name=display_name).first()
            if team_member is None:
                team_member = TeamMember(display_name=display_name)
                db.add(team_member)
                db.commit()
                db.refresh(team_member)

            # Create JiraUser linked to TeamMember
            jira_user = JiraUser(
                account_id=account_id,
                display_name=display_name,
                team_member_id=team_member.id
            )
            db.add(jira_user)
            db.commit()
            db.refresh(jira_user)

        if not jira_user:
            jira_user = JiraUser(
                id=str(uuid.uuid4()),
                account_id=account_id,
                display_name=display_name,
                email=email
            )
            db.add(jira_user)
            db.commit()

        # Resolve TeamMember via external identity, not email
        ext = db.query(TeamMemberExternalIdentity).filter_by(
            source="jira",
            external_id=account_id
        ).first()

        if ext:
            tm = db.query(TeamMember).filter_by(id=ext.team_member_id).first()
        else:
            tm = TeamMember(
                id=str(uuid.uuid4()),
                display_name=display_name,
                email=email  # may be None
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


        # Link JiraUser → TeamMember
        jira_user.team_member_id = tm.id

        db.commit()

        # -----------------------------------------------------
        # 5. Upsert JiraIssue
        # -----------------------------------------------------
        issue = db.query(JiraIssue).filter_by(issue_key=issue_key).first()
        if not issue:
            issue = JiraIssue(
                id=str(uuid.uuid4()),
                issue_key=issue_key
            )
            db.add(issue)

        # Update issue fields
        fields = payload["issue"]["fields"]
        issue.summary = fields.get("summary")
        issue.status = fields["status"]["name"]
        issue.issue_type = fields["issuetype"]["name"]
        issue.priority = fields["priority"]["name"]
        issue.updated_at = datetime.utcnow()

        db.commit()

        # -----------------------------------------------------
        # 6. Create JiraEvent
        # -----------------------------------------------------
        event = JiraEvent(
            id=str(uuid.uuid4()),
            issue_id=issue.id,
            event_type=event_type,
            raw_payload=payload,
            triggered_by_id=jira_user.id,  # still the actor
            timestamp=datetime.utcnow()
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # -----------------------------------------------------
        # 7. Extract behavioural signals
        # -----------------------------------------------------
        signals = extract_signals_from_event(event_type, payload)
        
        print("Extracted signals:", signals)

        for sig in signals:
            interaction = TeamMemberInteraction(
                id=str(uuid.uuid4()),
                team_member_id=jira_user.team_member_id,  # NOW THE ASSIGNEE
                jira_event_id=event.id,
                signal_type=sig["type"],
                weight=sig["weight"],
                event_metadata=sig.get("metadata"),
                timestamp=datetime.utcnow()
            )
            db.add(interaction)

        db.commit()

        # -----------------------------------------------------
        # 8. Trigger rule engine
        # -----------------------------------------------------
        evaluate_team_state({})

        return {"status": "ok", "received": True}

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()
