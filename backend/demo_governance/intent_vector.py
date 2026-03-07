import re
import hashlib

def extract_intent_vector(text: str):
    words = re.findall(r"[a-zA-Z]+", text.lower())

    verbs = [w for w in words if w.endswith("e") or w.endswith("ing")]
    negations = [w for w in words if w in ["not", "never", "no"]]

    signature = hashlib.sha256((" ".join(verbs + negations)).encode()).hexdigest()[:12]

    return {
        "verbs": verbs,
        "negations": negations,
        "signature": signature,
    }
