from app.saam.persona_compare import compare_personas

result = compare_personas({
    "silent": "silent_experiment.jsonl",
    "healthy": "healthy_experiment.jsonl",
    "blocked": "blocked_experiment.jsonl"
})

print(result)
