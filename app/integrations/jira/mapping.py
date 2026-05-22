from datetime import datetime, timezone

def map_jira_to_saam(issue: dict) -> dict:
    fields = issue.get("fields", {})

    # 1. Blocker age (days)
    created_str = fields.get("created")
    if created_str:
        created_dt = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - created_dt).days
    else:
        age_days = None

    # 2. Missing assignee
    assignee_missing = fields.get("assignee") is None

    # 3. Status
    status = fields.get("status", {}).get("name")

    # 4. Issue type
    issue_type = fields.get("issuetype", {}).get("name")

    # 5. Summary
    summary = fields.get("summary")

    # 6. Ceremony + time_remaining (placeholder for now)
    ceremony = "none"
    time_remaining = 1.0

    return {
        "blocker_age_days": age_days,
        "blocker_owner_missing": assignee_missing,
        "status": status,
        "issue_type": issue_type,
        "summary": summary,
        "ceremony": ceremony,
        "time_remaining": time_remaining
    }
