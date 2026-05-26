from datetime import datetime, timezone

def map_jira_to_saam(issue: dict) -> dict:
    """
    Map a raw Jira issue into SAAM's internal blocker/state format.
    Extracts:
    - blocker age (days)
    - owner missing flag
    - status, issue type, summary
    - default ceremony + time_remaining placeholders
    """

    if not issue:
        return {}

    fields = issue.get("fields", {})

    # --- Blocker age --------------------------------------------------------
    created_str = fields.get("created")
    if created_str:
        created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created_dt).days
    else:
        age_days = None

    # --- Basic metadata -----------------------------------------------------
    assignee_missing = fields.get("assignee") is None
    status = fields.get("status", {}).get("name")
    issue_type = fields.get("issuetype", {}).get("name")
    summary = fields.get("summary")

    # --- SAAM‑compatible output ---------------------------------------------
    return {
        "blocker_age_days": age_days,
        "blocker_owner_missing": assignee_missing,
        "status": status,
        "issue_type": issue_type,
        "summary": summary,

        # Defaults for downstream rule engines
        "ceremony": "none",
        "time_remaining": 1.0,
    }
