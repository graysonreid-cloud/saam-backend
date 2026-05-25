def calculate_confidence(decisions, best, state=None) -> float:
    """
    Confidence Engine v2:
    - base: rule priority
    - agreement: how many rules fired
    - contrast: gap to second-best rule
    - category agreement: how many rules share best's category
    - signal strength: uses normalised signals if state is provided
    """
    if not best or not decisions:
        return 0.0

    # ---------- 1. BASE: RULE PRIORITY ----------
    best_priority = best.get("priority", 0) or 0
    base_score = best_priority / 10.0  # priority 8 → 0.8

    # ---------- 2. AGREEMENT: NUMBER OF RULES FIRED ----------
    rule_count = len(decisions)
    agreement_score = min(rule_count / 10.0, 0.3)  # cap at +0.3

    # ---------- 3. CONTRAST: GAP TO SECOND-BEST ----------
    ordered = sorted(decisions, key=lambda d: d.get("priority", 0) or 0, reverse=True)
    if len(ordered) > 1:
        second_best = ordered[1]
        gap = best_priority - (second_best.get("priority", 0) or 0)
        if gap >= 3:
            contrast_score = 0.3
        elif gap == 2:
            contrast_score = 0.2
        elif gap == 1:
            contrast_score = 0.1
        else:
            contrast_score = 0.0
    else:
        # Only one rule fired → reasonably clear situation
        contrast_score = 0.2

    # ---------- 4. CATEGORY AGREEMENT ----------
    best_cat = best.get("rule_category")
    same_cat = [d for d in decisions if d.get("rule_category") == best_cat]
    cat_count = len(same_cat)
    if cat_count >= 3:
        category_score = 0.2
    elif cat_count == 2:
        category_score = 0.1
    else:
        category_score = 0.0

    # ---------- 5. SIGNAL STRENGTH (NORMALISED SIGNALS) ----------
    signal_score = 0.0
    if state:
        participation = state.get("participation_norm", 0.0) or 0.0
        imbalance = state.get("imbalance_norm", 0.0) or 0.0
        blocker_age = state.get("blocker_age_norm", 0.0) or 0.0
        time_urgency = state.get("time_remaining_norm", 0.0) or 0.0

        # Strong dysfunction → higher confidence
        severity = max(
            1.0 - participation,  # low participation
            imbalance,
            blocker_age,
            time_urgency,
        )
        signal_score = 0.3 * severity  # up to +0.3

    # ---------- 6. COMBINE & CLAMP ----------
    confidence = (
        base_score
        + agreement_score
        + contrast_score
        + category_score
        + signal_score
    )

    return max(0.0, min(confidence, 1.0))
