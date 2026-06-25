def compute_collaboration_score(stats: dict) -> int:
    """
    MVP: Simple deterministic collaboration score.
    Score = comments + assignments + transitions
    """
    return (
        stats.get("comments", 0)
        + stats.get("assignments", 0)
        + stats.get("transitions", 0)
    )
