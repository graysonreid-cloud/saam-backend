import csv
import os
from datetime import datetime, timezone

LOG_PATH = "saam_log.csv"

# Ensure the log file exists with headers
if not os.path.exists(LOG_PATH):
    with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "timestamp",
            "cue",
            "priority",
            "message",
            "explanation",
            "rule_name",
            "rule_category",
            "rule_version",
            "rationale",
            "raw_json"
        ])


def log_intervention(intervention: dict, raw_json: str):
    """Append a structured SAAM log entry."""
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now(timezone.utc).isoformat(),
            intervention.get("cue"),
            intervention.get("priority"),
            intervention.get("message"),
            intervention.get("explanation"),
            intervention.get("rule_name"),
            intervention.get("rule_category"),
            intervention.get("rule_version"),
            intervention.get("rationale"),
            raw_json
        ])


