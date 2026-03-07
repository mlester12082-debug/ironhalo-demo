from demo_governance.clauses import Clause, CLAUSE_TITLES, INLINE_PRECEDENT

def generate_ruling(clause: Clause, deviation_summary: str):
    if clause == Clause.CLAUSE_3:
        decision = "Clause 3 invoked — intent vector shows minor contradiction; correction applied."
    elif clause == Clause.CLAUSE_5:
        decision = "Clause 5 invoked — intent vector shows significant deviation; correction applied."
    else:
        decision = "Clause 7 invoked — intent vector shows structural contradiction; correction applied."

    rationale = INLINE_PRECEDENT[clause]
    clause_title = CLAUSE_TITLES[clause]

    return decision, rationale, clause_title
