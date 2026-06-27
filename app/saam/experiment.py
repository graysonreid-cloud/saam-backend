# app/saam/experiment.py

import random
from .interaction import run_interaction_round
from .logging import log_interaction


def generate_random_raw_stats(persona: str) -> dict:
    """
    Generate random behavioural stats for a persona.
    These feed into cue extraction.
    """

    if persona == "silent":
        return {
            "participation_level": random.uniform(0.0, 0.3),
            "talktime_imbalance": random.uniform(0.5, 0.9),
            "blocker_age": random.uniform(0, 2),
            "missing_updates": True,
            "blocker_owner_missing": False,
            "time_remaining": random.uniform(3, 8),
            "goal_changes": 0,
            "ceremony_type": "standup",
            "sentiment_score": random.uniform(-0.2, 0.2),
            "workload_ratio": random.uniform(0.8, 1.0),
            "help_requests": 0,
            "help_offers": 0,
        }

    if persona == "healthy":
        return {
            "participation_level": random.uniform(0.7, 1.0),
            "talktime_imbalance": random.uniform(0.0, 0.2),
            "blocker_age": random.uniform(0, 1),
            "missing_updates": False,
            "blocker_owner_missing": False,
            "time_remaining": random.uniform(3, 8),
            "goal_changes": 0,
            "ceremony_type": "standup",
            "sentiment_score": random.uniform(0.2, 0.8),
            "workload_ratio": random.uniform(0.8, 1.2),
            "help_requests": random.randint(0, 1),
            "help_offers": random.randint(1, 3),
        }

    if persona == "blocked":
        return {
            "participation_level": random.uniform(0.2, 0.5),
            "talktime_imbalance": random.uniform(0.2, 0.5),
            "blocker_age": random.uniform(3, 10),
            "missing_updates": True,
            "blocker_owner_missing": True,
            "time_remaining": random.uniform(1, 5),
            "goal_changes": random.randint(0, 1),
            "ceremony_type": "standup",
            "sentiment_score": random.uniform(-0.6, -0.1),
            "workload_ratio": random.uniform(1.2, 1.8),
            "help_requests": random.randint(1, 4),
            "help_offers": 0,
        }

    raise ValueError(f"Unknown persona: {persona}")


def run_experiment(persona: str, rounds: int = 20, log_file: str = "experiment.jsonl"):
    """
    Run N rounds of SAAM ↔ Persona interaction and log each round.
    """

    results = []

    for _ in range(rounds):
        raw_stats = generate_random_raw_stats(persona)
        record = run_interaction_round(persona, raw_stats)
        log_interaction(record, filename=log_file)
        results.append(record)

    # Summary calculations
    avg_sentiment = (
        sum(r["sentiment_estimate"] for r in results) / rounds
        if rounds > 0 else 0
    )

    predicted_label_counts = {
        "silent": sum(1 for r in results if r["predicted_label"] == "silent"),
        "healthy": sum(1 for r in results if r["predicted_label"] == "healthy"),
        "blocked": sum(1 for r in results if r["predicted_label"] == "blocked"),
    }

    return {
        "persona": persona,
        "rounds": rounds,
        "log_file": log_file,
        "summary": {
            "avg_sentiment": avg_sentiment,
            "predicted_label_counts": predicted_label_counts,
        },
    }
