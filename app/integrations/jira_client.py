import os
import requests


# ---------------------------------------------------------
# Load Jira credentials
# ---------------------------------------------------------

JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")


def _check_credentials():
    if not (JIRA_BASE_URL and JIRA_EMAIL and JIRA_API_TOKEN):
        raise RuntimeError("Jira credentials are not configured in environment variables.")


def _auth_headers():
    return {
        "Accept": "application/json"
    }


# ---------------------------------------------------------
# Fetch a single Jira issue
# ---------------------------------------------------------

def fetch_jira_issue(issue_key: str):
    """
    Fetch a Jira issue using basic auth.
    Returns the raw requests.Response object.
    """
    _check_credentials()

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers=_auth_headers()
    )

    return response


# ---------------------------------------------------------
# Fetch Jira user by accountId
# ---------------------------------------------------------

def fetch_jira_user(account_id: str):
    """
    Fetch a Jira user by accountId.
    """
    _check_credentials()

    url = f"{JIRA_BASE_URL}/rest/api/3/user?accountId={account_id}"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers=_auth_headers()
    )

    return response


# ---------------------------------------------------------
# Fetch comments for an issue
# ---------------------------------------------------------

def fetch_issue_comments(issue_key: str):
    """
    Fetch all comments for a Jira issue.
    """
    _check_credentials()

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers=_auth_headers()
    )

    return response


# ---------------------------------------------------------
# Fetch changelog (status changes, assignments, etc.)
# ---------------------------------------------------------

def fetch_issue_changelog(issue_key: str):
    """
    Fetch the changelog for a Jira issue.
    """
    _check_credentials()

    url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/changelog"

    response = requests.get(
        url,
        auth=(JIRA_EMAIL, JIRA_API_TOKEN),
        headers=_auth_headers()
    )

    return response
