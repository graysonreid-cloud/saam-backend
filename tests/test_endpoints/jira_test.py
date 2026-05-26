from fastapi import APIRouter, HTTPException
from app.integrations.jira_client import fetch_jira_issue
from app.integrations.jira.mapping import map_jira_to_saam

router = APIRouter()

@router.get("/jira/test/{issue_key}")
def test_jira(issue_key: str):
    response = fetch_jira_issue(issue_key)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    issue_json = response.json()
    saam_state = map_jira_to_saam(issue_json)

    return {
        "raw_jira": issue_json,
        "saam_mapped": saam_state
    }
