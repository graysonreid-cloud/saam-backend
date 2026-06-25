# app/engine/signals.py

from unittest import signals


def extract_signals_from_event(event_type: str, payload: dict):
    """
    Convert Jira webhook events into SAAM behavioural signals.
    Returns a list of dicts:
    [
        {
            "type": "comment_created",
            "weight": 1.0,
            "metadata": {...}
        }
    ]
    """

    signals = []

    # ---------------------------------------------------------
    # COMMENT CREATED (Jira Cloud native event)
    # ---------------------------------------------------------
    if event_type == "comment_created" and "comment" in payload:
        comment = payload["comment"]
        signals.append({
            "type": "comment_created",
            "weight": 1.0,
            "metadata": {
                "body": comment.get("body"),
                "author": comment.get("author", {}).get("displayName")
            }
        })
        return signals

    # ---------------------------------------------------------
    # ISSUE CREATED
    # ---------------------------------------------------------
    if event_type == "jira:issue_created":
        issue = payload.get("issue", {})
        signals.append({
            "type": "issue_created",
            "weight": 1.5,
            "metadata": {
                "issue_key": issue.get("key"),
                "summary": issue.get("fields", {}).get("summary")
            }
        })
        return signals

    # ---------------------------------------------------------
    # ISSUE UPDATED (changelog)
    # ---------------------------------------------------------
    if event_type == "jira:issue_updated":
        changelog = payload.get("changelog", {})
        items = changelog.get("items", [])

        for item in items:
            field = item.get("field")
            from_val = item.get("fromString")
            to_val = item.get("toString")

            # COMMENT ADDED (via changelog)
            if field == "comment":
                signals.append({
                    "type": "comment_created",
                    "weight": 1.0,
                    "metadata": {
                        "from": from_val,
                        "to": to_val
                    }
                })
                continue

            # ASSIGNMENT CHANGE
            if field == "assignee":
                signals.append({
                    "type": "assignment_changed",
                    "weight": 1.2,
                    "metadata": {
                        "from": from_val,
                        "to": to_val
                    }
                })
                continue

            # STATUS TRANSITION
            if field == "status":
                weight = 2.0 if to_val and to_val.lower() == "blocked" else 1.0
                signals.append({
                    "type": "status_transition",
                    "weight": weight,
                    "metadata": {
                        "from": from_val,
                        "to": to_val
                    }
                })
                continue

            # GENERIC FIELD EDIT
            signals.append({
                "type": "field_edited",
                "weight": 0.5,
                "metadata": {
                    "field": field,
                    "from": from_val,
                    "to": to_val
                }
            })

        return signals

    # ---------------------------------------------------------
    # DEFAULT: no signals
    # ---------------------------------------------------------
    return signals
