from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from demo_governance.engine import (
    run_governed_strike,
    run_config_strike,
    EVENT_LOG
)

# ---------------------------------------------------------
# FastAPI App + CORS
# ---------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # allow frontend on localhost or public link
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Framing Line (Landing Route)
# ---------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "IronHalo is a perimeter intelligence that adapts to your behavior in real time."
    }

# ---------------------------------------------------------
# Request Models
# ---------------------------------------------------------

class GovernInput(BaseModel):
    action: str

class ConfigInput(BaseModel):
    config: str

# ---------------------------------------------------------
# AI MISBEHAVIOR GOVERNANCE ENDPOINT
# ---------------------------------------------------------

@app.post("/govern")
def govern(req: GovernInput):
    summary = req.action
    result = run_governed_strike("IH-1.2", summary)

    return {
        "ruling": f"{result['clause_title']} — {result['decision']}",
        "boundary_pressure": "medium" if result["pattern_detected"] != "NONE" else "low",
        "perimeter_state": result["boundary_state"],
        "drift_value": 0.6 if result["pattern_detected"] != "NONE" else 0.2,
        "intent_strength": 0.7 if result["pattern_detected"] != "NONE" else 0.3,
        "perimeter_index": 0 if result["boundary_state"] == "TIGHTENED" else 1,
        "drift_vectors": "0.60" if result["pattern_detected"] != "NONE" else "0.20",
        "capsules": [
            f"event: {result['pattern_detected']}",
            f"boundary: {result['boundary_state']}",
            f"replay: {result['replay_token']}",
        ],
    }

# ---------------------------------------------------------
# UNIVERSAL CLOUD MISCONFIG GOVERNANCE ENDPOINT
# ---------------------------------------------------------

@app.post("/config")
def config_govern(req: ConfigInput):
    cfg = req.config
    result = run_config_strike(cfg)

    tampered = result["pattern_detected"] == "CONFIG_TAMPERING"
    severity = 1.0 if tampered else 0.2

    return {
        "ruling": f"{result['clause_title']} — {result['decision']}",
        "boundary_pressure": "high" if tampered else "low",
        "perimeter_state": result["boundary_state"],
        "drift_value": severity,
        "intent_strength": min(severity + 0.1, 1.0),
        "perimeter_index": 0 if tampered else 1,
        "drift_vectors": f"{severity:.2f}",
        "capsules": [
            f"finding: {result['pattern_detected']}",
            f"boundary: {result['boundary_state']}",
            f"replay: {result['replay_token']}",
        ],
    }

# ---------------------------------------------------------
# FORENSIC LOG (LAST 50 EVENTS)
# ---------------------------------------------------------

@app.get("/forensics")
def get_forensics():
    return list(EVENT_LOG)
