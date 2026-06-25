from app.saam.analysis import load_logs
from app.saam.effectiveness import intervention_effectiveness

records = load_logs("silent_experiment.jsonl")
table = intervention_effectiveness(records)

print(table)
