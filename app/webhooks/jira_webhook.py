from fastapi import APIRouter, Request, HTTPException
import traceback

from app.integrations.jira.mapping import map_jira_to_saam
from app.engine.evaluator import evaluate_team_state
from db.database import SessionLocal
from services.identity_service import resolve_identity

router = APIRouter()


@router.post("/jira")
async def jira_webhook(request: Request):
    db = SessionLocal()
    try:
        payload = await request.json()
        print("JIRA PAYLOAD:", payload)

        issue = payload.get("issue")
        user = payload.get("user") or {}

        # -------------------------------
        # ACTOR (person who performed the action)
        # -------------------------------
        actor_account_id = user.get("accountId", "unknown")
        actor_display_name = user.get("displayName", "Unknown User")
        actor_email = user.get("emailAddress") or f"{actor_account_id}@jira.local"

        actor_member = resolve_identity(
            db=db,
            source="jira",
            external_id=actor_account_id,   # ← ACTOR identity key
            display_name=actor_display_name,
            email=actor_email
        )

        # -------------------------------
        # ASSIGNEE (person the issue is assigned to)
        # -------------------------------
        assignee = issue.get("fields", {}).get("assignee")
        assignee_member = None

        if assignee:
            assignee_account_id = assignee.get("accountId")
            assignee_display_name = assignee.get("displayName")
            assignee_email = assignee.get("emailAddress") or f"{assignee_account_id}@jira.local"

            assignee_member = resolve_identity(
                db=db,
                source="jira",
                external_id=assignee_account_id,   # ← ASSIGNEE identity key
                display_name=assignee_display_name,
                email=assignee_email
            )

        # -------------------------------
        # Map Jira → SAAM
        # -------------------------------
        saam_state = map_jira_to_saam(issue) or {}

        # Actor info
        saam_state["actor_id"] = str(actor_member.id)
        saam_state["actor_name"] = actor_member.display_name
        saam_state["actor_email"] = actor_member.email

        # Assignee info
        if assignee_member:
            saam_state["assignee_id"] = str(assignee_member.id)
            saam_state["assignee_name"] = assignee_member.display_name
            saam_state["assignee_email"] = assignee_member.email
        else:
            saam_state["assignee_id"] = None
            saam_state["assignee_name"] = None
            saam_state["assignee_email"] = None

        saam_state["issue"] = issue
        saam_state["event_type"] = payload.get("webhookEvent")

        # Evaluate (Jira guard will short-circuit)
        decision = evaluate_team_state(saam_state)
        print("EVALUATOR DECISION OK")

        return {
            "status": "ok",
            "saam_state": saam_state,
            "decision": decision
        }

    except Exception as e:
        print("JIRA ERROR:", repr(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        db.close()
