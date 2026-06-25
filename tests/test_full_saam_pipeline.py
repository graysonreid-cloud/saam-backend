from db.database import SessionLocal
from app.services.member_aggregation import aggregate_member_interactions
from app.services.collaboration_score import compute_collaboration_score
from app.engine.perceptron_predict import predict_label
from app.services.saam_output import build_saam_output

def run_test():
    print("=== SAAM FULL PIPELINE TEST ===")

    db = SessionLocal()

    # 1. Aggregate Jira behaviour
    print("\n[1] Aggregating member interactions...")
    members = aggregate_member_interactions(db)
    print("Aggregated:", members)

    # 2. Compute collaboration scores
    print("\n[2] Computing collaboration scores...")
    for m in members:
        score = compute_collaboration_score(m)
        print(m["display_name"], "-> score:", score)

    # 3. Predict perceptron labels
    print("\n[3] Predicting perceptron labels...")
    for m in members:
        label = predict_label(m)
        print(m["display_name"], "-> label:", label)

    # 4. Build full SAAM output
    print("\n[4] Building SAAM output...")
    output = build_saam_output(db)
    print(output)

    print("\n=== PIPELINE COMPLETE ===")

if __name__ == "__main__":
    run_test()
