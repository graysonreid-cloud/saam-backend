from app.saam.analysis import load_logs, analyse_logs

records = load_logs("silent_experiment.jsonl")
summary = analyse_logs(records)

print(summary)
