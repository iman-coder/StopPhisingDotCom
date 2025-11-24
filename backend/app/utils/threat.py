from typing import Optional
import re


def normalize_threat(threat: Optional[str]) -> str:
    """Normalize freeform threat text into one of:
    'malicious', 'suspicious', 'safe', or 'unknown'.

    Steps:
    - handle None/empty -> 'unknown'
    - lowercase and replace punctuation/underscores with spaces
    - keyword-based heuristics (substring matching)

    This is intentionally lightweight; expand keywords as needed.
    """
    if not threat:
        return "unknown"

    # normalize: lowercase and replace non-alphanum with spaces
    t = threat.strip().lower()
    t = re.sub(r"[^a-z0-9]+", " ", t)

    # direct canonical forms (exact tokens)
    tokens = t.split()
    if any(tok in ("malicious", "high", "phishing", "phish", "malware", "malwaredownload") for tok in tokens):
        return "malicious"
    if any(tok in ("suspicious", "susp", "low") for tok in tokens):
        return "suspicious"
    if any(tok in ("safe", "none", "clean", "benign") for tok in tokens):
        return "safe"

    # keyword heuristics (substring matches) for broader coverage
    if any(k in t for k in ("phish", "malware", "exploit", "ransom", "trojan", "virus", "bot", "rogueware", "malicious", "credential", "steal", "download", "redirect", "inject", "fraud", "spam")):
        return "malicious"
    if any(k in t for k in ("susp", "maybe", "uncertain", "review", "warn")):
        return "suspicious"
    if any(k in t for k in ("ok", "safe", "legit", "benign", "clean")):
        return "safe"

    return "unknown"
