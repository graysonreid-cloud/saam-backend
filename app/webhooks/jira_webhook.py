from fastapi import APIRouter, Request, HTTPException
from app.integrations.jira.mapping import map_jira_to_saam
from app.rules.evaluator import evaluate_state  # your existing evaluator

router = APIRouter()

@router.post("/jira")
async def jira_webhook(request: Request):
    try:
        payload = await request.json()

        issue = payload.get("issue")
        if not issue:
            raise HTTPException(status_code=400, detail="Missing issue in webhook payload")

        # Map Jira → SAAM schema
        saam_state = map_jira_to_saam(issue)

        # Evaluate using your rule engine
        result = evaluate_state(saam_state)

        # TODO: send result to Teams, log to DB, etc.
        print("SAAM decision:", result)

        return {"status": "ok", "saam_state": saam_state, "decision": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
