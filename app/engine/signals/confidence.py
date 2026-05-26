def calculate_confidence(decisions, best, state=None) -> float:
    """
    Confidence Engine
    Combines rule priority, agreement, contrast, category alignment,
    and signal severity into a 0–1 confidence score.
    """

    if not best or not decisions:
        return 0.0

    # --- 1. Base confidence from rule priority ------------------------------
    best_priority = best.get("priority", 0)
    base_score = best_priority / 10.0  # e.g., priority 8 → 0.8

    # --- 2. Agreement: how many rules fired --------------------------------
    agreement_score = min(len(decisions) / 10.0, 0.3)

    # --- 3. Contrast: gap to second‑best rule -------------------------------
    ordered = sorted(decisions, key=lambda d: d.get("priority", 0), reverse=True)

    if len(ordered) > 1:
        gap = best_priority - ordered[1].get("priority", 0)
        contrast_score = {3: 0.3, 2: 0.2, 1: 0.1}.get(gap, 0.0)
    else:
        contrast_score = 0.2  # only one rule fired → clear signal

    # --- 4. Category agreement ----------------------------------------------
    best_cat = best.get("rule_category")
    same_cat = sum(1 for d in decisions if d.get("rule_category") == best_cat)
    category_score = 0.2 if same_cat >= 3 else 0.1 if same_cat == 2 else 0.0

    # --- 5. Signal strength (normalised metrics) ----------------------------
    signal_score = 0.0
    if state:
        participation = state.get("participation_norm", 0.0)
        imbalance = state.get("imbalance_norm", 0.0)
        blocker_age = state.get("blocker_age_norm", 0.0)
        time_urgency = state.get("time_remaining_norm", 0.0)

        # Strong dysfunction → higher confidence
        severity = max(
            1.0 - participation,  # low participation
            imbalance,
            blocker_age,
            time_urgency,
        )
        signal_score = 0.3 * severity  # up to +0.3

    # --- 6. Combine and clamp -----------------------------------------------
    confidence = base_score + agreement_score + contrast_score + category_score + signal_score
    return max(0.0, min(confidence, 1.0))
