import os
import requests

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

def fetch_jira_issue(issue_key: str):
    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"}
    )

    return response
