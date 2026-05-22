import os
import requests

JIRA_BASE_URL = os.getenv("https://graysonreid.atlassian.net/")
JIRA_USERNAME = os.getenv("graysonreid@gmail.com")
JIRA_API_TOKEN = os.getenv("REMOVED3xFfGF0bYByeDTAr3LSrvk8hGGh-TorcH0oM45zcXabG0neKREuQBBqDGJzwWZ-SVkyAhuWeJ-S85MlJUO6XyX0DLAoxOK6lYIwYdMKRY-EMf7q5sSoXxnq4EgN1-niUFiSnwv4foLWiEZ8xqrc49kfsOTP2q5pMCCrfPWWDQYURxjLx4w=9C0DBB4C")

def fetch_jira_issue(issue_key: str):
    if not all([JIRA_BASE_URL, JIRA_USERNAME, JIRA_API_TOKEN]):
        return {
            "error": "Jira credentials not configured",
            "issue_key": issue_key,
            "data": None
        }

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    try:
        response = requests.get(
            url,
            auth=(JIRA_USERNAME, JIRA_API_TOKEN),
            headers={"Accept": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        return {
            "error": str(e),
            "issue_key": issue_key,
            "data": None
        }



