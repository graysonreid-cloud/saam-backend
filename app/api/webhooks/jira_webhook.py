from fastapi import APIRouter, Request
from sqlalchemy.orm import Session
import json

from db.database import SessionLocal
from db.db_models import (
    Request as SAAMRequest,
    JiraUser, JiraIssue, JiraEvent,
    TeamMember, TeamMemberExternalIdentity,
    TeamMemberInteraction
)

from app.engine.signals import extract_signals_from_event

# SAAM ENGINE
from app.saam.jira_adapter import jira_to_stats
from app.saam.cues import extract_cues
from app.saam.features import build_feature_vector
from app.saam.actions import select_action
from app.saam.interaction import sentiment_score
from app.saam.message_templates import apply_sprint_context_prefix
from app.saam.logging import log_interaction


import joblib
import uuid
from datetime import datetime, timezone

router = APIRouter()


# ---------------------------------------------------------
# Helper: Jira datetime parser
# ---------------------------------------------------------
def parse_jira_datetime(dt_str: str):
    """
    Jira returns timestamps like:
    - 2025-01-12T09:00:00.000+0000
    - 2025-01-12T09:00:00.000Z

    Python requires:
    - +00:00 instead of +0000
    """
    if not dt_str:
        return None

    # Convert +0000 → +00:00
    if dt_str.endswith("+0000"):
        dt_str = dt_str[:-5] + "+00:00"

    # Convert Z → +00:00
    dt_str = dt_str.replace("Z", "+00:00")

    return datetime.fromisoformat(dt_str)


# ---------------------------------------------------------
# Webhook endpoint
# ---------------------------------------------------------

@router.post("/jira")
async def jira_webhook(request: Request):
    db: Session = SessionLocal()

    try:
        payload = await request.json()
        print("Webhook Event:", payload.get("webhookEvent"))

        # -----------------------------------------------------
        # EVENT FILTERING
        # -----------------------------------------------------
        event_type = payload.get("webhookEvent")
        changelog = payload.get("changelog", {})
        items = changelog.get("items", [])

        if "comment" in payload:
            print("Detected comment event")

        elif any(item.get("field") == "assignee" for item in items):
            print("Detected assignee change")

        elif any(item.get("field") == "status" for item in items):
            print("Detected status change")

        elif event_type == "worklog_updated":
            print("Detected worklog update")

        else:
            print(f"Ignoring non-behavioural event: {event_type}")
            return {"status": "ignored_event"}

        # -----------------------------------------------------
        # 1. Log raw request
        # -----------------------------------------------------
        req = SAAMRequest(
            id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
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
        issue_fields = payload.get("issue", {}).get("fields", {})

        # -----------------------------------------------------
        # 3. Determine behavioural subject
        # -----------------------------------------------------
        assignee = issue_fields.get("assignee")

        if assignee:
            account_id = assignee.get("accountId")
            display_name = assignee.get("displayName")
            email = assignee.get("emailAddress")
        else:
            actor = payload.get("user", {})
            account_id = actor.get("accountId")
            display_name = actor.get("displayName")
            email = actor.get("emailAddress")

        # -----------------------------------------------------
        # 4. Resolve JiraUser → TeamMember
        # -----------------------------------------------------
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

        jira_user = db.query(JiraUser).filter_by(account_id=account_id).first()

        if not jira_user:
            jira_user = JiraUser(
                id=str(uuid.uuid4()),
                account_id=account_id,
                display_name=display_name,
                email=email,
                team_member_id=tm.id
            )
            db.add(jira_user)
        else:
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

        issue.summary = issue_fields.get("summary")
        issue.status = issue_fields["status"]["name"]
        issue.issue_type = issue_fields["issuetype"]["name"]
        issue.priority = issue_fields["priority"]["name"]
        issue.updated_at = datetime.now(timezone.utc)

        db.commit()

        # -----------------------------------------------------
        # 6. Create JiraEvent
        # -----------------------------------------------------
        event = JiraEvent(
            id=str(uuid.uuid4()),
            issue_id=issue.id,
            event_type=event_type,
            raw_payload=payload,
            triggered_by_id=jira_user.id,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(event)
        db.commit()
        db.refresh(event)

        # -----------------------------------------------------
        # 7. Extract behavioural signals
        # -----------------------------------------------------
        signals = extract_signals_from_event(event_type, payload)

        for sig in signals:
            interaction = TeamMemberInteraction(
                id=str(uuid.uuid4()),
                team_member_id=jira_user.team_member_id,
                jira_event_id=event.id,
                signal_type=sig["type"],
                weight=sig["weight"],
                event_metadata=sig.get("metadata"),
                timestamp=datetime.now(timezone.utc)
            )
            db.add(interaction)

        db.commit()

        # -----------------------------------------------------
        # 8. SAAM ENGINE
        # -----------------------------------------------------

        jira_rows = db.query(JiraEvent).join(
            JiraUser, JiraEvent.triggered_by_id == JiraUser.id
        ).filter(
            JiraUser.team_member_id == jira_user.team_member_id
        ).all()

        jira_dicts = [row.to_dict() for row in jira_rows]

        stats = jira_to_stats(jira_dicts)

        # -----------------------------------------------------
        # SPRINT CONTEXT EXTRACTION (fixed)
        # -----------------------------------------------------
        try:
            sprint_data = issue_fields.get("customfield_10020", [])
            active_sprint = next((s for s in sprint_data if s.get("state") == "active"), None)

            sprint_context = {}
            now = datetime.now(timezone.utc)

            if active_sprint:
                sprint_start = parse_jira_datetime(active_sprint.get("startDate"))
                sprint_end = parse_jira_datetime(active_sprint.get("endDate"))

                if sprint_start and sprint_end:
                    total_days = max((sprint_end - sprint_start).days, 1)
                    days_remaining = max((sprint_end - now).days, 0)
                    sprint_progress = round(1 - (days_remaining / total_days), 2)

                    sprint_context.update({
                        "sprint_start": active_sprint.get("startDate"),
                        "sprint_end": active_sprint.get("endDate"),
                        "total_days": total_days,
                        "days_remaining": days_remaining,
                        "sprint_progress": sprint_progress
                    })

            created_dt = parse_jira_datetime(issue_fields.get("created"))
            status_dt = parse_jira_datetime(issue_fields.get("statuscategorychangedate"))

            if created_dt:
                sprint_context["issue_age_days"] = (now - created_dt).days

            if status_dt:
                sprint_context["time_in_status_days"] = (now - status_dt).days

            stats["sprint_context"] = sprint_context

        except Exception as e:
            print("Sprint context extraction failed:", e)

        # -----------------------------------------------------
        # 8. SAAM ENGINE
        # -----------------------------------------------------

        # Extract cues (now includes risk_score)
        cues = extract_cues(stats)

        # Build feature vector
        X = build_feature_vector(cues)

        # Predict behavioural label
        model = joblib.load("models/perceptron.pkl")["model"]
        pred = model.predict(X)[0]
        label_map = {0: "silent", 1: "healthy", 2: "blocked"}
        predicted_label = label_map[pred]

        # Select intervention (risk-aware)
        action = select_action(predicted_label, cues)

        # Sprint-aware prefix
        action["message"] = apply_sprint_context_prefix(action["message"], cues)

        # Sentiment estimate
        sentiment = sentiment_score(action["message"])


        print("\n================ SAAM ENGINE OUTPUT ================")
        print("Team Member ID:", jira_user.team_member_id)
        print("Display Name:", display_name)
        print("Predicted Label:", predicted_label)
        print("Cues:", json.dumps(cues, indent=2))
        print("Risk Score:", cues.get("risk_score"))
        print("Intervention Type:", action["intervention_type"])
        print("Action:", action["action"])
        print("Message:", action["message"])
        print("Sentiment Estimate:", sentiment)
        print("====================================================\n")

        # Correct logging call
        log_interaction({
            "persona": display_name,
            "predicted_label": predicted_label,
            "risk_score": cues.get("risk_score"),
            "intervention_type": action["intervention_type"],
            "action": action["action"],
            "saam_message": action["message"],
            "cues": cues
        })
        # -----------------------------------------------------
        # 9. Return SAAM action
        # -----------------------------------------------------
        return {
            "status": "ok",
            "received": True,
            "team_member_id": jira_user.team_member_id,
            "predicted_label": predicted_label,
            "cues": cues,
            "intervention_type": action["intervention_type"],
            "action": action["action"],
            "message": action["message"],
            "sentiment_estimate": sentiment
        }

    except Exception as e:
        db.rollback()
        raise e

    finally:
        db.close()
