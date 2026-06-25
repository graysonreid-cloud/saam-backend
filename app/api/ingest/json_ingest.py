from fastapi import APIRouter, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from db.database import SessionLocal
import json

from app.services.jira_ingest import process_jira_issue

router = APIRouter()

@router.post("/ingest/json")
async def ingest_json_dump(file: UploadFile = File(...)):
    """
    MVP: Accept a JSON export of Jira issues and process them
    using the same ingestion pipeline as live webhooks.
    """
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    raw = await file.read()

    try:
        data = json.loads(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON format")

    issues = data.get("issues", [])
    if not issues:
        raise HTTPException(status_code=400, detail="No issues found in JSON")

    db: Session = SessionLocal()
    processed = 0

    for issue in issues:
        normalized = {
            "issue": issue,
            "user": issue.get("user", {}),
            "webhookEvent": issue.get("webhookEvent", "jira:issue_updated")
        }

    process_jira_issue(db, normalized)
    processed += 1


    db.commit()

    return {
        "status": "ok",
        "issues_processed": processed
    }
