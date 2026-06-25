# app/saam/results.py

from .analysis import load_logs, analyse_logs

def sentiment_summary_table(summary: dict):
    return [
        {"Metric": "Rounds", "Value": summary["rounds"]},
        {"Metric": "Average Sentiment", "Value": round(summary["avg_sentiment"], 3)},
        {"Metric": "Minimum Sentiment", "Value": round(summary["sentiment_min"], 3)},
        {"Metric": "Maximum Sentiment", "Value": round(summary["sentiment_max"], 3)},
    ]


def label_distribution_table(summary: dict):
    dist = summary["label_distribution"]
    return [
        {"Label": "Silent", "Count": dist["silent"]},
        {"Label": "Healthy", "Count": dist["healthy"]},
        {"Label": "Blocked", "Count": dist["blocked"]},
    ]


def intervention_distribution_table(summary: dict):
    dist = summary["intervention_distribution"]
    return [
        {"Intervention Type": "Soft", "Count": dist["soft"]},
        {"Intervention Type": "Hard", "Count": dist["hard"]},
        {"Intervention Type": "None", "Count": dist["none"]},
    ]


def generate_all_tables(log_filename: str):
    """
    Load logs, analyse them, and generate all results tables.
    """
    records = load_logs(log_filename)
    summary = analyse_logs(records)

    return {
        "sentiment_summary": sentiment_summary_table(summary),
        "label_distribution": label_distribution_table(summary),
        "intervention_distribution": intervention_distribution_table(summary),
    }
