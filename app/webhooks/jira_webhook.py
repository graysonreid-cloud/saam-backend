from fastapi import APIRouter, Request, HTTPException
from app.integrations.jira.mapping import map_jira_to_saam
from app.engine.evaluator import evaluate_team_state
from db.database import SessionLocal
from services.identity_service import resolve_identity

router = APIRouter()


@router.post("/jira")
async def jira_webhook(request: Request):
    try:

        payload = await request.json()
        issue = payload.get("issue")
        user = payload.get("user")
        db = SessionLocal()

        account_id = user.get("accountId")
        display_name = user.get("displayName")
        email = user.get("emailAddress") or f"{account_id}@jira.local"

        member = resolve_identity(
            db=db,
            source="jira",
            external_id=account_id,
            display_name=display_name,
            email=email
        )

        # ---------------------------------------------------------
        # 2. Map Jira → SAAM state
        # ---------------------------------------------------------
        saam_state = map_jira_to_saam(issue)

        # Inject identity into SAAM state
        saam_state["actor_id"] = str(member.id)
        saam_state["actor_name"] = member.display_name
        saam_state["actor_email"] = member.email

        # ---------------------------------------------------------
        # 3. Evaluate rules
        # ---------------------------------------------------------
        decision = evaluate_team_state(saam_state)

        # ---------------------------------------------------------
        # 4. Close DB session
        # ---------------------------------------------------------
        db.close()

        # ---------------------------------------------------------
        # 5. Return enriched output
        # ---------------------------------------------------------
        return {
            "status": "ok",
            "saam_state": saam_state,
            "decision": decision
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
