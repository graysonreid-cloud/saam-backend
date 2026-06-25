# app/saam/persona_compare.py

from .analysis import load_logs, analyse_logs

def compare_personas(log_files: dict):
    """
    Compare multiple personas using their experiment log files.

    log_files = {
        "silent": "silent_experiment.jsonl",
        "healthy": "healthy_experiment.jsonl",
        "blocked": "blocked_experiment.jsonl"
    }
    """

    comparison = []

    for persona, filename in log_files.items():
        records = load_logs(filename)
        summary = analyse_logs(records)

        comparison.append({
            "Persona": persona,
            "Rounds": summary["rounds"],
            "Avg Sentiment": round(summary["avg_sentiment"], 3),
            "Silent %": round(summary["label_distribution"]["silent"] / summary["rounds"], 2),
            "Healthy %": round(summary["label_distribution"]["healthy"] / summary["rounds"], 2),
            "Blocked %": round(summary["label_distribution"]["blocked"] / summary["rounds"], 2),
            "Soft %": round(summary["intervention_distribution"]["soft"] / summary["rounds"], 2),
            "Hard %": round(summary["intervention_distribution"]["hard"] / summary["rounds"], 2),
            "None %": round(summary["intervention_distribution"]["none"] / summary["rounds"], 2),
        })

    return comparison
