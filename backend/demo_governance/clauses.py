from enum import Enum

class Clause(Enum):
    CLAUSE_3 = 3
    CLAUSE_5 = 5
    CLAUSE_7 = 7

CLAUSE_TITLES = {
    Clause.CLAUSE_3: "Early Drift — Minor Contradiction",
    Clause.CLAUSE_5: "Significant Deviation — Moderate Contradiction",
    Clause.CLAUSE_7: "Structural Breach — High Contradiction",
}

INLINE_PRECEDENT = {
    Clause.CLAUSE_3: "Precedent detected — early drift previously observed.",
    Clause.CLAUSE_5: "Precedent detected — deviation matches a known pattern.",
    Clause.CLAUSE_7: "Precedent detected — structural contradiction previously logged.",
}

REPLAY_PRECEDENT = {
    Clause.CLAUSE_3: "Replay index: 1 prior early‑drift event.",
    Clause.CLAUSE_5: "Replay index: 2 prior moderate‑deviation events.",
    Clause.CLAUSE_7: "Replay index: prior structural‑contradiction event recorded.",
}
