from pydantic import BaseModel
import hashlib
import time
from collections import deque

# ---------------------------------------------------------------------------
# Rolling Constitutional Memory (Last 50 Events)
# ---------------------------------------------------------------------------

EVENT_LOG = deque(maxlen=50)

# ---------------------------------------------------------------------------
# Session State (Ephemeral, Demo-Scale)
# ---------------------------------------------------------------------------

SESSION_STATE = {
    "last_deviation": None,
    "repetition_count": 0,
    "contradiction_count": 0,
    "bypass_count": 0,
    "config_tamper_count": 0,
}

# ---------------------------------------------------------------------------
# Clause Registry (Demo-Scale)
# ---------------------------------------------------------------------------

CLAUSES = {
    "IH-1.1": "Boundary Formation",
    "IH-1.2": "Deviation Recognition",
    "IH-2.1": "Containment Protocol",
    "IH-3.4": "Replay-Native Accountability",
    "IH-4.2": "Configuration Integrity",
}

# ---------------------------------------------------------------------------
# Result Model
# ---------------------------------------------------------------------------

class GovernedStrikeResult(BaseModel):
    clause_id: str
    clause_title: str
    decision: str
    rationale: str
    replay_token: str
    boundary_state: str
    pattern_detected: str
    pattern_consequence: str

# ---------------------------------------------------------------------------
# Deviation Interpretation (Risk-Level)
# ---------------------------------------------------------------------------

def interpret_deviation(text: str) -> str:
    t = text.lower()

    if any(w in t for w in ["bypass", "override", "ignore", "circumvent"]):
        return "HIGH_RISK"

    if any(w in t for w in ["unclear", "maybe", "not sure", "confusing"]):
        return "AMBIGUOUS"

    if any(w in t for w in ["test", "demo", "example"]):
        return "LOW_RISK"

    return "NEUTRAL"

# ---------------------------------------------------------------------------
# Pattern Detection (Big Four)
# ---------------------------------------------------------------------------

def detect_pattern(text: str) -> str:
    t = text.lower()

    # Contradiction traps
    if any(w in t for w in ["contradict", "but earlier", "you said", "inconsistent"]):
        return "CONTRADICTION"

    # Boundary bypass attempts
    if any(w in t for w in ["break the rule", "ignore the rule", "make an exception"]):
        return "BYPASS"

    # Repetition exploits
    if SESSION_STATE["last_deviation"] == t:
        return "REPETITION"

    return "NONE"

# ---------------------------------------------------------------------------
# Config Tampering Detection
# ---------------------------------------------------------------------------

def detect_config_tampering(config_text: str) -> bool:
    """
    Demo-scale config tampering detector.
    This is where we wire in recognizable cloud-misconfig patterns so the
    IronHalo demo lights up on realistic configs (S3, NSG, etc.).
    """
    t = config_text.lower()

    # Existing demo patterns
    if "allow_override = true" in t:
        return True
    if "risk_threshold = 0" in t:
        return True
    if "boundary_sensitivity" in t and "high" in t:
        return True
    if "delete" in t or "remove" in t:
        return True
    if "admin" in t or "root" in t or "superuser" in t:
        return True

    # -----------------------------------------------------------------------
    # New: Test #1 – S3 anti-forensic pattern (expiration days = 0)
    # -----------------------------------------------------------------------
    # Terraform / JSON / YAML variants that effectively destroy logs immediately.
    if "expiration" in t and "days" in t and "0" in t:
        # This is intentionally coarse: any expiration + days + 0 combo
        # is treated as an anti-forensic configuration in the demo.
        return True

    # -----------------------------------------------------------------------
    # Hardened: Azure NSG public exposure detection (alias + CIDR + arrays)
    # -----------------------------------------------------------------------
    # Normalize the text once
    tl = t.lower()

    # Public exposure aliases used by Azure NSG
    public_aliases = [
        "internet",
        "any",
        "*",
        "0.0.0.0/0",
    ]

    # Keys Azure uses for NSG rules (singular + plural)
    nsg_keys = [
        "sourceaddressprefix",
        "sourceaddressprefixes",
        "destinationaddressprefix",
        "destinationaddressprefixes",
        "sourceportrange",
        "sourceportranges",
        "destinationportrange",
        "destinationportranges",
    ]

    # If any NSG key appears AND any public alias appears → exposure
    if any(k in tl for k in nsg_keys) and any(alias in tl for alias in public_aliases):
        return True

    # Also catch explicit 0.0.0.0/0 exposure anywhere in the config
    if "0.0.0.0/0" in tl:
        return True

    return False

# ---------------------------------------------------------------------------
# Pattern Consequence Logic
# ---------------------------------------------------------------------------

def apply_pattern_consequence(pattern: str) -> str:
    if pattern == "CONTRADICTION":
        SESSION_STATE["contradiction_count"] += 1
        return "INCONSISTENCY_DETECTED"

    if pattern == "BYPASS":
        SESSION_STATE["bypass_count"] += 1
        return "BOUNDARY_DEFENSE"

    if pattern == "REPETITION":
        SESSION_STATE["repetition_count"] += 1
        return "REPETITION_IMMUNITY"

    if pattern == "CONFIG_TAMPERING":
        SESSION_STATE["config_tamper_count"] += 1
        return "CONFIG_DEFENSE"

    return "NONE"

# ---------------------------------------------------------------------------
# Boundary Tightening
# ---------------------------------------------------------------------------

def boundary_tightening(signal: str) -> str:
    if signal == "HIGH_RISK":
        return "TIGHTENED"
    if signal == "AMBIGUOUS":
        return "OBSERVED"
    if signal == "LOW_RISK":
        return "UNCHANGED"
    return "STABLE"

# ---------------------------------------------------------------------------
# Replay Token Generator
# ---------------------------------------------------------------------------

def generate_replay_token(clause_id: str, deviation: str) -> str:
    raw = f"{clause_id}|{deviation}|{int(time.time())}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"replay::{clause_id}::{digest}"

# ---------------------------------------------------------------------------
# Main Strike (AI Misbehavior)
# ---------------------------------------------------------------------------

def run_governed_strike(clause_id: str, deviation_summary: str) -> dict:
    clause_prefix = clause_id.split()[0] if " " in clause_id else clause_id
    clause_title = CLAUSES.get(clause_prefix, "Unknown Clause")

    # Risk interpretation
    signal = interpret_deviation(deviation_summary)

    # Pattern detection
    pattern = detect_pattern(deviation_summary)
    pattern_consequence = apply_pattern_consequence(pattern)

    # Boundary state
    boundary_state = boundary_tightening(signal)

    # Update session memory
    SESSION_STATE["last_deviation"] = deviation_summary.lower()

    # Decision + rationale
    decision = "CONTAINED_AND_RECORDED"
    rationale = (
        f"Deviation interpreted as {signal}. "
        f"Pattern detected: {pattern}. "
        f"Consequence applied: {pattern_consequence}. "
        f"Clause {clause_id} ({clause_title}) applied. "
        f"Boundary state: {boundary_state}. Replay token issued."
    )

    replay_token = generate_replay_token(clause_id, deviation_summary)

    result = GovernedStrikeResult(
        clause_id=clause_id,
        clause_title=clause_title,
        decision=decision,
        rationale=rationale,
        replay_token=replay_token,
        boundary_state=boundary_state,
        pattern_detected=pattern,
        pattern_consequence=pattern_consequence,
    ).model_dump()

    # Log event
    EVENT_LOG.append({
        "type": "behavior",
        "pattern": pattern,
        "boundary": boundary_state,
        "decision": decision,
        "clause": clause_title,
        "replay": replay_token,
        "timestamp": int(time.time()),
    })

    return result

# ---------------------------------------------------------------------------
# Config Strike (Cloud Misconfig)
# ---------------------------------------------------------------------------

def run_config_strike(config_text: str) -> dict:
    tampered = detect_config_tampering(config_text)

    clause_id = "IH-4.2"
    clause_title = CLAUSES[clause_id]

    if tampered:
        pattern = "CONFIG_TAMPERING"
        pattern_consequence = apply_pattern_consequence(pattern)
        boundary_state = "TIGHTENED"
    else:
        pattern = "NONE"
        pattern_consequence = "NONE"
        boundary_state = "STABLE"

    rationale = (
        f"Configuration integrity check performed. "
        f"Pattern detected: {pattern}. "
        f"Consequence applied: {pattern_consequence}. "
        f"Boundary state: {boundary_state}. "
        f"Clause {clause_id} ({clause_title}) applied."
    )

    replay_token = generate_replay_token(clause_id, config_text)

    result = GovernedStrikeResult(
        clause_id=clause_id,
        clause_title=clause_title,
        decision="CONFIG_REVIEWED",
        rationale=rationale,
        replay_token=replay_token,
        boundary_state=boundary_state,
        pattern_detected=pattern,
        pattern_consequence=pattern_consequence,
    ).model_dump()

    # Log event
    EVENT_LOG.append({
        "type": "config",
        "pattern": pattern,
        "boundary": boundary_state,
        "decision": "CONFIG_REVIEWED",
        "clause": clause_title,
        "replay": replay_token,
        "timestamp": int(time.time()),
    })

    return result
