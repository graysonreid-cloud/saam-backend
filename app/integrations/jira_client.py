import os
import requests

# Load Jira credentials from environment
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def fetch_jira_issue(issue_key: str):
    """
    Fetch a Jira issue using basic auth.
    Returns the raw requests.Response object for upstream handling.
    """

    if not (JIRA_BASE_URL and JIRA_EMAIL and JIRA_API_TOKEN):
        raise RuntimeError("Jira credentials are not configured in environment variables.")

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers={"Accept": "application/json"}
    )

    return response
