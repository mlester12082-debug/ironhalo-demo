from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from demo_governance.engine import run_governed_strike, run_config_strike
import time
import hashlib

app = FastAPI(title="IronHalo Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Request / Response Models
# -----------------------------

class StrikeRequest(BaseModel):
    clause_id: str
    deviation_summary: str

class ConfigRequest(BaseModel):
    config_text: str

class StrikeResponse(BaseModel):
    clause_id: str
    clause_title: str
    decision: str
    rationale: str
    replay_token: str
    boundary_state: str
    pattern_detected: str
    pattern_consequence: str

# -----------------------------
# Forensics Log
# -----------------------------

EVENT_LOG = []

def compute_drift_signature(text: str) -> str:
    """
    Simple drift signature:
    Hash of the text (verbs/negations would be extracted in a full engine).
    """
    return hashlib.sha256(text.encode()).hexdigest()[:16]  # short fingerprint

# -----------------------------
# Health Check
# -----------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# -----------------------------
# Strike Endpoint
# -----------------------------

@app.post("/strike", response_model=StrikeResponse)
def strike(req: StrikeRequest):
    result = run_governed_strike(req.clause_id, req.deviation_summary)

    drift_sig = compute_drift_signature(req.deviation_summary)

    EVENT_LOG.append({
        "timestamp": time.time(),
        "type": "strike",
        "input": {
            "clause_id": req.clause_id,
            "deviation_summary": req.deviation_summary
        },
        "output": result,
        "drift_signature": drift_sig,
        "boundary_state": result.boundary_state,
        "pattern_detected": result.pattern_detected,
        "replay_token": result.replay_token
    })

    return result

# -----------------------------
# Config Strike Endpoint
# -----------------------------

@app.post("/config-strike", response_model=StrikeResponse)
def config_strike(req: ConfigRequest):
    result = run_config_strike(req.config_text)

    drift_sig = compute_drift_signature(req.config_text)

    EVENT_LOG.append({
        "timestamp": time.time(),
        "type": "config-strike",
        "input": req.config_text,
        "output": result,
        "drift_signature": drift_sig,
        "boundary_state": result.boundary_state,
        "pattern_detected": result.pattern_detected,
        "replay_token": result.replay_token
    })

    return result

# -----------------------------
# Forensics Endpoint
# -----------------------------

@app.get("/forensics")
def forensics():
    # Return the last 50 events
    return EVENT_LOG[-50:]
