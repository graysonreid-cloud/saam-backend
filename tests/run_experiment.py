from app.saam.experiment import run_experiment

result = run_experiment("silent", rounds=20, log_file="silent_experiment.jsonl")
print(result)

result = run_experiment("blocked", rounds=20, log_file="blocked_experiment.jsonl")
print(result)

result = run_experiment("healthy", rounds=20, log_file="healthy_experiment.jsonl")
print(result)