from app.services.member_aggregation import aggregate_member_interactions
from app.services.collaboration_score import compute_collaboration_score
from app.engine.perceptron_predict import predict_label

def build_saam_output(db):
    """
    Builds the full SAAM output for all team members.
    This is the final step in the SAAM pipeline:
      - Aggregated Jira behaviour
      - Collaboration score
      - Perceptron classification
    """

    members = aggregate_member_interactions(db)
    results = []

    for stats in members:
        score = compute_collaboration_score(stats)
        label = predict_label(stats)

        results.append({
            "user_id": stats["user_id"],
            "display_name": stats["display_name"],
            "comments": stats["comments"],
            "assignments": stats["assignments"],
            "transitions": stats["transitions"],
            "collaboration_score": score,
            "saam_label": label
        })

    return results
