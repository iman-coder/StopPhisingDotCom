from typing import Optional
import re


def normalize_threat(threat: Optional[object]) -> str:
    """Normalize freeform threat text into one of:
    'malicious', 'suspicious', 'safe', or 'unknown'.

    Steps:
    - handle None/empty -> 'unknown'
    - lowercase and replace punctuation/underscores with spaces
    - keyword-based heuristics (substring matching)

    This is intentionally lightweight; expand keywords as needed.
    """
    # Treat None or empty-like values as unknown
    if threat is None:
        return "unknown"

    # normalize: coerce to string, lowercase and replace non-alphanum with spaces
    t = str(threat).strip().lower()
    if not t:
        return "unknown"
    t = re.sub(r"[^a-z0-9]+", " ", t)

    # direct canonical forms (exact tokens)
    tokens = t.split()
    if any(tok in ("malicious", "high", "phishing", "phish", "malware", "malwaredownload") for tok in tokens):
        return "malicious"
    if any(tok in ("suspicious", "susp", "medium","moderate") for tok in tokens):
        return "suspicious"
    if any(tok in ("safe", "none", "clean", "benign","no risk","low") for tok in tokens):
        return "safe"

    # keyword heuristics (substring matches) for broader coverage
    if any(k in t for k in ("very high","high","phish", "malware", "exploit", "ransom", "trojan", "virus", "bot", "rogueware", "malicious", "credential", "steal", "download", "redirect", "inject", "fraud", "spam")):
        return "malicious"
    if any(k in t for k in ("susp", "maybe", "uncertain", "review", "warn","caution", "questionable", "risk","adware","potentially unwanted","medium","moderate")):
        return "suspicious"
    if any(k in t for k in ("ok", "safe", "legit", "benign", "clean","trusted","very low","no risk","low","harmless")):
        return "safe"

    return "suspicious"  # default to suspicious if unclear


def risk_score(threat: Optional[str]) -> int:
    """Return a numeric risk score (0-100) for a given freeform threat string.

    This provides a simple, explainable mapping from the normalized threat
    category to a numeric score useful for UI quantification. Scores are
    intentionally coarse and can be tuned later.
    """
    norm = normalize_threat(threat)
    mapping = {
        "malicious": 90,
        "suspicious": 55,
        "safe": 10,
        "unknown": 40,
    }
    return int(mapping.get(norm, 50))
