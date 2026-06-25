# app/saam/analysis.py

import json
import os
from statistics import mean

def load_logs(filename: str):
    """
    Load a JSONL experiment log file into a list of dicts.
    """
    path = os.path.join("interaction_logs", filename)

    if not os.path.exists(path):
        raise FileNotFoundError(f"Log file not found: {path}")

    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            records.append(json.loads(line))

    return records


def analyse_logs(records: list):
    """
    Compute summary statistics from experiment logs.
    """

    sentiments = [r["sentiment"] for r in records]
    predicted_labels = [r["predicted_label"] for r in records]
    intervention_types = [r["intervention_type"] for r in records]

    return {
        "rounds": len(records),
        "avg_sentiment": mean(sentiments),
        "sentiment_min": min(sentiments),
        "sentiment_max": max(sentiments),
        "label_distribution": {
            "silent": predicted_labels.count("silent"),
            "healthy": predicted_labels.count("healthy"),
            "blocked": predicted_labels.count("blocked")
        },
        "intervention_distribution": {
            "soft": intervention_types.count("soft"),
            "hard": intervention_types.count("hard"),
            "none": intervention_types.count("none")
        }
    }
