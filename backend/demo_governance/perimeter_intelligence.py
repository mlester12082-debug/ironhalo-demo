def evaluate_boundary(clause_id: int):
    # Minor contradiction → relaxed boundary
    if clause_id == 3:
        return "RELAXED"

    # Moderate or high contradiction → tightened boundary
    if clause_id == 5:
        return "TIGHTENED"

    return "TIGHTENED"
