from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uuid
import re

app = FastAPI(title="IronHalo Engine Demo")

# Allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigStrikeRequest(BaseModel):
    config_text: str

# In‑memory forensic log
forensic_log: List[Dict[str, Any]] = []


# -----------------------------
# Helper: Parse override flag
# -----------------------------
def parse_override_flag(text: str) -> bool:
    """
    Extracts allow_override value safely.
    Only returns True if explicitly set to true.
    """
    match = re.search(r"allow_override\s*=\s*(\S+)", text.lower())
    if not match:
        return False

    value = match.group(1).strip().lower()
    return value == "true"


# -----------------------------
# Pattern Detection Logic
# -----------------------------
def detect_pattern(config_text: str) -> Dict[str, Any]:
    text = config_text.lower()
    patterns = []

    # AWS
    if "aws_s3_bucket" in text and "public-read" in text:
        patterns.append("aws_public_s3")

    # Azure
    if "networksecuritygroup" in text and "sourceaddressprefix" in text and '"*"' in text:
        patterns.append("azure_open_nsg")

    # GCP
    if "firewall" in text and "0.0.0.0/0" in text:
        patterns.append("gcp_open_firewall")

    # Universal override attempt (fixed)
    override_flag = parse_override_flag(text)
    if override_flag:
        patterns.append("universal_override_attempt")

    # No misconfig
    if not patterns:
        patterns.append("no_obvious_misconfig")

    # Clause selection
    if "universal_override_attempt" in patterns:
        clause_id = "Clause 7"
        clause_title = "Universal Override Immunity"
        decision = "DENY"
        boundary_state = "TIGHTEN"
        drift_severity = "HIGH"
        rationale = "Detected explicit override attempt against perimeter constraints."

    elif any(p in patterns for p in ["aws_public_s3", "azure_open_nsg", "gcp_open_firewall"]):
        clause_id = "Clause 3"
        clause_title = "Public Surface Minimization"
        decision = "DENY"
        boundary_state = "TIGHTEN"
        drift_severity = "MEDIUM"
        rationale = "Detected public exposure of critical surface across one or more cloud providers."

    else:
        clause_id = "Clause 1"
        clause_title = "Baseline Constitutional Readiness"
        decision = "ALLOW"
        boundary_state = "IMMUNE"
        drift_severity = "LOW"
        rationale = "No material misconfiguration detected relative to current perimeter."

    return {
        "patterns": patterns,
        "clause_id": clause_id,
        "clause_title": clause_title,
        "decision": decision,
        "boundary_state": boundary_state,
        "drift_severity": drift_severity,
        "rationale": rationale,
    }


# -----------------------------
# /config-strike
# -----------------------------
@app.post("/config-strike")
def config_strike(req: ConfigStrikeRequest):
    analysis = detect_pattern(req.config_text)

    replay_token = str(uuid.uuid4())[:8]
    drift_value = 0.7 if analysis["boundary_state"] == "TIGHTEN" else 0.2
    intent_strength = 0.8 if "override" in req.config_text.lower() else 0.4
    perimeter_index = 0 if analysis["boundary_state"] == "TIGHTEN" else 1

    event = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "clause_id": analysis["clause_id"],
        "clause_title": analysis["clause_title"],
        "decision": analysis["decision"],
        "boundary_state": analysis["boundary_state"],
        "pattern_detected": ", ".join(analysis["patterns"]),
        "rationale": analysis["rationale"],
        "replay_token": replay_token,
        "drift_value": drift_value,
        "intent_strength": intent_strength,
        "perimeter_index": perimeter_index,
    }

    forensic_log.append(event)
    if len(forensic_log) > 100:
        forensic_log.pop(0)

    return event


# -----------------------------
# /forensics
# -----------------------------
@app.get("/forensics")
def get_forensics():
    return {"events": forensic_log}
