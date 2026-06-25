# app/saam/logging.py

import json
import os
from datetime import datetime

LOG_DIR = "interaction_logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_interaction(record: dict, filename: str = "experiment.jsonl"):
    """
    Append a single interaction record to a JSONL log file.
    """
    record_with_timestamp = {
        "timestamp": datetime.utcnow().isoformat(),
        **record
    }

    path = os.path.join(LOG_DIR, filename)

    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record_with_timestamp) + "\n")

    return path
