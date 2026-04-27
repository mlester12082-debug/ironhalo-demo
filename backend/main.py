from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import uuid
import re

app = FastAPI(title="IronHalo Engine Demo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConfigStrikeRequest(BaseModel):
    config_text: str

forensic_log: List[Dict[str, Any]] = []


# -----------------------------
# Helpers
# -----------------------------
def strip_comments(text: str) -> str:
    """
    Best-effort removal of full-line and trailing comments for common formats.
    This keeps us from firing on obvious commented-out junk.
    """
    cleaned_lines = []
    for line in text.splitlines():
        # Remove // and # comments
        line_no_inline = re.split(r"(#|//)", line, maxsplit=1)[0]
        if line_no_inline.strip():
            cleaned_lines.append(line_no_inline)
    return "\n".join(cleaned_lines)


def parse_override_flag(text: str) -> bool:
    """
    Extracts allow_override value safely.
    Only returns True if explicitly set to true/yes/1 (case-insensitive).
    """
    match = re.search(r"\ballow_override\s*=\s*(\S+)", text, re.IGNORECASE)
    if not match:
        return False
    value = match.group(1).strip().lower()
    return value in ["true", "yes", "1"]


# -----------------------------
# Pattern Detection Logic
# -----------------------------
def detect_pattern(config_text: str) -> Dict[str, Any]:
    # Work on original and comment-stripped versions
    raw_text = config_text
    text_no_comments = strip_comments(config_text)
    text_lower = text_no_comments.lower()

    # Strip zero-width / invisible Unicode chars
    text_lower = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff]", "", text_lower)

    # Normalize common Unicode homoglyphs to ASCII
    homoglyph_map = {
        "і": "i",  # Cyrillic small i
        "І": "i",  # Cyrillic capital i
        "е": "e",
        "Е": "e",
        "а": "a",
        "А": "a",
        "о": "o",
        "О": "o",
        "с": "c",
        "С": "c",
        "р": "p",
        "Р": "p",
        "х": "x",
        "Х": "x",
    }
    for bad, good in homoglyph_map.items():
        text_lower = text_lower.replace(bad, good)

    # Collapse all whitespace to defeat multi-line / unicode whitespace evasions
    text_compact = re.sub(r"\s+", "", text_lower)

    patterns = []

    # -------------------------
    # AWS — S3 anti-forensic (expiration days = 0)
    # -------------------------
    if re.search(
        r"expiration\s*[:=]?\s*[{]?\s*[\s\S]*?days\s*[:=]\s*0\b",
        text_no_comments,
        re.IGNORECASE,
    ):
        patterns.append("s3_anti_forensic_expiration_0")

    # -------------------------
    # AWS — public S3
    # -------------------------
    if re.search(r"aws_s3_bucket", text_lower) and re.search(
        r"\bpublic-read\b|\bpublic-read-write\b", text_lower
    ):
        patterns.append("aws_public_s3")

    # -------------------------
    # AWS — IAM wildcard
    # -------------------------
    if re.search(r'"action"\s*:\s*"\*"', text_no_comments, re.IGNORECASE) or re.search(
        r"\baction\s*=\s*\"?\*\"?", text_no_comments, re.IGNORECASE
    ):
        patterns.append("aws_iam_wildcard")

    # -------------------------
    # Azure — open NSG (hardened, quote- and whitespace-agnostic)
    # -------------------------
    if re.search(
        r"(source|destination)[_]?address[_]?prefix(es)?",
        text_lower,
    ):
        if re.search(
            r"(\*|0\.0\.0\.0/0|internet|any)",
            text_compact,
            re.IGNORECASE,
        ):
            patterns.append("azure_open_nsg")

    # -------------------------
    # Azure — NSG context alias (deep nesting, non-standard keys)
    # -------------------------
    if "securityrules" in text_compact:
        if re.search(r"(internet|any|0\.0\.0\.0/0|\*)", text_compact, re.IGNORECASE):
            patterns.append("azure_nsg_context_alias")

    # -------------------------
    # GCP — open firewall
    # -------------------------
    if re.search(r"firewall", text_lower) and re.search(
        r"0\.0\.0\.0/0", text_no_comments
    ):
        patterns.append("gcp_open_firewall")

    # -------------------------
    # Universal open CIDR
    # -------------------------
    if re.search(r"0\.0\.0\.0/0", text_no_comments):
        patterns.append("universal_open_cidr")

    # -------------------------
    # Kubernetes — privilege escalation
    # -------------------------
    if re.search(
        r"privileged\s*:\s*(true|\"true\"|True|\"True\")",
        text_no_comments,
        re.IGNORECASE,
    ):
        patterns.append("k8s_priv_escalation")

    if re.search(
        r"allowprivilegeescalation\s*:\s*(true|\"true\"|\"TRUE\"|True)",
        text_no_comments,
        re.IGNORECASE,
    ):
        patterns.append("k8s_priv_escalation")

    # -------------------------
    # YAML / JSON public flags
    # -------------------------
    if re.search(
        r"\bpublic\s*:\s*(true|\"true\"|True|\"True\")",
        text_no_comments,
        re.IGNORECASE,
    ):
        patterns.append("yaml_public_flag")

    if re.search(
        r'"public"\s*:\s*(true|"true"|True|"True")',
        text_no_comments,
        re.IGNORECASE,
    ):
        patterns.append("json_public_flag")

    # -------------------------
    # Override / intent signals
    # -------------------------
    override_flag = parse_override_flag(text_no_comments)

    if re.search(
        r"\boverride\s*[:=]\s*(true|yes|1)\b", text_no_comments, re.IGNORECASE
    ) and not override_flag:
        patterns.append("override_intent")

    if override_flag:
        patterns.append("universal_override_attempt")

    # -------------------------
    # No misconfig
    # -------------------------
    if not patterns:
        patterns.append("no_obvious_misconfig")

    # -------------------------
    # Clause selection priority
    # -------------------------

    # 1) Explicit override attempts
    if "universal_override_attempt" in patterns or "override_intent" in patterns:
        clause_id = "Clause 7"
        clause_title = "Universal Override Immunity"
        decision = "DENY"
        boundary_state = "TIGHTEN"
        drift_severity = "HIGH"
        rationale = "Detected explicit or implicit override attempt against perimeter constraints."

    # 2) High‑risk privilege / wildcard / open surface / anti-forensic
    elif any(
        p
        in [
            "k8s_priv_escalation",
            "aws_iam_wildcard",
            "universal_open_cidr",
            "yaml_public_flag",
            "json_public_flag",
            "aws_public_s3",
            "azure_open_nsg",
            "azure_nsg_context_alias",
            "gcp_open_firewall",
            "s3_anti_forensic_expiration_0",
        ]
        for p in patterns
    ):
        if "k8s_priv_escalation" in patterns:
            clause_id = "Clause 5"
            clause_title = "Workload Privilege Boundaries"
            decision = "DENY"
            boundary_state = "TIGHTEN"
            drift_severity = "MEDIUM"
            rationale = "Detected Kubernetes workload requesting privilege escalation or privileged execution."
        else:
            clause_id = "Clause 3"
            clause_title = "Public Surface Minimization"
            decision = "DENY"
            boundary_state = "TIGHTEN"
            drift_severity = "MEDIUM"
            rationale = "Detected public exposure, wildcard access, or anti-forensic configuration across one or more surfaces."

    # 3) Baseline readiness (SAFE CONFIGS)
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
