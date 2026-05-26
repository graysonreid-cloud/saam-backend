from fastapi import APIRouter, Request, HTTPException
import traceback

from app.integrations.jira.mapping import map_jira_to_saam
from app.engine.evaluator import evaluate_team_state
from db.database import SessionLocal
from app.services.identity_service import resolve_identity

router = APIRouter()


@router.post("/jira")
async def jira_webhook(request: Request):
    db = SessionLocal()
    try:
        payload = await request.json()
        issue = payload.get("issue", {})
        user = payload.get("user", {})

        # Resolve actor (person performing the action)
        actor_member = resolve_identity(
            db=db,
            source="jira",
            external_id=user.get("accountId", "unknown"),
            display_name=user.get("displayName", "Unknown User"),
            email=user.get("emailAddress") or f"{user.get('accountId', 'unknown')}@jira.local"
        )

        # Resolve assignee (if present)
        assignee = issue.get("fields", {}).get("assignee")
        assignee_member = None

        if assignee:
            assignee_member = resolve_identity(
                db=db,
                source="jira",
                external_id=assignee.get("accountId"),
                display_name=assignee.get("displayName"),
                email=assignee.get("emailAddress") or f"{assignee.get('accountId')}@jira.local"
            )

        # Map Jira → SAAM state
        saam_state = map_jira_to_saam(issue) or {}

        saam_state.update({
            "actor_id": str(actor_member.id),
            "actor_name": actor_member.display_name,
            "actor_email": actor_member.email,
            "assignee_id": str(assignee_member.id) if assignee_member else None,
            "assignee_name": assignee_member.display_name if assignee_member else None,
            "assignee_email": assignee_member.email if assignee_member else None,
            "issue": issue,
            "event_type": payload.get("webhookEvent")
        })

        decision = evaluate_team_state(saam_state)

        return {
            "status": "ok",
            "saam_state": saam_state,
            "decision": decision
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
