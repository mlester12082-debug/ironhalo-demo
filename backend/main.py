from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from demo_governance.engine import run_governed_strike, run_config_strike

app = FastAPI(title="IronHalo Demo Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/strike", response_model=StrikeResponse)
def strike(req: StrikeRequest):
    return run_governed_strike(req.clause_id, req.deviation_summary)

@app.post("/config-strike", response_model=StrikeResponse)
def config_strike(req: ConfigRequest):
    return run_config_strike(req.config_text)
