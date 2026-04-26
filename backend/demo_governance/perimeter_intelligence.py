def evaluate_boundary(clause_id: int):
    """
    Boundary intelligence for IronHalo.
    Maps constitutional clause outcomes to perimeter states.
    This version supports:
      - Clause 3  → minor contradiction → RELAXED
      - Clause 5  → major contradiction → TIGHTENED
      - Clause 7  → structural contradiction → LOCKDOWN
      - IH‑4.2 (config tampering) → TIGHTENED
      - Everything else → STABLE
    """

    # Clause 3 — Minor contradiction
    if clause_id == 3:
        return "RELAXED"

    # Clause 5 — Significant contradiction
    if clause_id == 5:
        return "TIGHTENED"

    # Clause 7 — Structural contradiction (highest severity)
    if clause_id == 7:
        return "LOCKDOWN"

    # IH‑4.2 — Config integrity violations (cloud misconfigs)
    if clause_id == 42:  # mapped from IH‑4.2 → 4.2 → 42
        return "TIGHTENED"

    # Default
    return "STABLE"
