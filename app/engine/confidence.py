def calculate_confidence(decisions, best):
    if not decisions or not best:
        return 0.0

    # 1. Normalised priority strength (0–1)
    max_priority = max(d["priority"] for d in decisions)
    priority_strength = best["priority"] / max_priority if max_priority > 0 else 0

    # 2. Rule agreement (how many rules fired)
    rule_count = len(decisions)
    rule_agreement = min(rule_count / 5, 1)  # cap at 5 rules

    # 3. Priority spread (consistency)
    priorities = [d["priority"] for d in decisions]
    spread = max(priorities) - min(priorities)
    consistency = 1 - min(spread / 10, 1)  # large spread = low consistency

    # Weighted confidence score
    confidence = (
        0.5 * priority_strength +
        0.3 * rule_agreement +
        0.2 * consistency
    )

    return round(confidence, 3)
