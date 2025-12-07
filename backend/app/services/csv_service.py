# app/services/csv_service.py

import csv
from io import StringIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import URL
from app.schemas import URLCreate
from app.utils.logger import get_logger
from app.utils.threat import normalize_threat, risk_score

logger = get_logger(__name__)


# -------- CSV IMPORT -------- #

def import_csv(file_content: str, db: Session):
    # Try to detect delimiter (comma/semicolon/tab) to be tolerant of different CSV formats
    sample = file_content[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[',', ';', '\t'])
        delim = dialect.delimiter
    except Exception:
        delim = ','

    reader = csv.DictReader(StringIO(file_content), delimiter=delim)
    created_count = 0
    skipped = []

    # preload existing URLs from DB to avoid unique constraint violations
    existing_urls = set([r[0] for r in db.query(URL.url).all()]) if db.query(URL).count() > 0 else set()
    seen = set()

    # Log the detected header keys (normalized) to aid debugging
    try:
        raw_fieldnames = reader.fieldnames or []
        norm_fieldnames = [fn.strip().lower() if fn else fn for fn in raw_fieldnames]
        logger.info("import_csv: detected delimiter='%s' headers=%s", delim, raw_fieldnames)
        logger.debug("import_csv: normalized headers=%s", norm_fieldnames)
    except Exception:
        logger.debug("import_csv: could not read headers")

    def _parse_risk_field(val):
        """Parse a CSV risk/threat field which may be textual ('high','malicious')
        or numeric ('90', '55') and return a canonical threat label.

        Numeric thresholds (coarse):
          >= 75 -> 'malicious'
          40-74 -> 'suspicious'
          < 40  -> 'safe'
        """
        if val is None:
            return None
        if isinstance(val, (int, float)):
            score = int(val)
            if score >= 75:
                return "malicious"
            if score >= 40:
                return "suspicious"
            return "safe"
        # string value: try numeric parse first
        s = str(val).strip()
        if s == "":
            return None
        # Try parse as integer/float
        try:
            n = float(s)
            return _parse_risk_field(int(n))
        except Exception:
            # fallback: treat as textual threat and normalize
            return normalize_threat(s)

    for row in reader:
        # Normalize row keys (case-insensitive, trim) and values
        norm_row = { (k.strip().lower() if k else k): (v.strip() if isinstance(v, str) else v) for k, v in (row.items() if row else []) }
        # Accept 'url' column in any case / with spaces
        url_value = norm_row.get("url") or norm_row.get("link") or norm_row.get("uri")
        if not url_value:
            skipped.append(norm_row)
            continue

        # Avoid duplicate URLs (both in DB and already seen in this import)
        if url_value in existing_urls or url_value in seen:
            skipped.append(norm_row)
            continue

        # normalize threat text so stored values are canonical
        # Accept multiple column names that might provide risk info
        raw_threat = norm_row.get("threat") or norm_row.get("risk") or norm_row.get("risk_score") or norm_row.get("score")
        # parse numeric/textual risk into canonical label
        normalized = _parse_risk_field(raw_threat) or normalize_threat(raw_threat)

        # Compute numeric risk_score to store (preserve numeric if present,
        # otherwise map textual labels to coarse scores via `risk_score()`)
        numeric_score = None
        if raw_threat is not None:
            # try numeric parse first
            try:
                n = float(str(raw_threat).strip())
                # clamp to 0-100 and store integer value
                numeric_score = max(0, min(100, int(n)))
            except Exception:
                # textual -> use helper mapping
                try:
                    numeric_score = int(max(0, min(100, risk_score(str(raw_threat)))))
                except Exception:
                    numeric_score = None
        new_url = URL(
            url=url_value,
            domain=norm_row.get("domain") or norm_row.get("host"),
            threat=normalized,
            risk_score=numeric_score,
            status=norm_row.get("status"),
            source=norm_row.get("source"),
        )

        db.add(new_url)
        created_count += 1
        seen.add(url_value)

    db.commit()

    logger.info("import_csv: inserted=%s skipped=%s", created_count, len(skipped))
    if skipped:
        # log up to 10 skipped rows for debugging (show normalized rows)
        logger.debug("import_csv skipped rows sample: %s", skipped[:10])

    return {
        "inserted": created_count,
        "skipped": len(skipped),
    }


# -------- CSV EXPORT -------- #

def export_csv(db: Session) -> str:
    urls = db.query(URL).all()

    output = StringIO()
    writer = csv.writer(output)

    # CSV header (include risk_score if present)
    writer.writerow(["id", "url", "domain", "threat", "risk_score", "date_added", "status", "source"])

    # CSV rows
    for item in urls:
        writer.writerow([
            item.id,
            item.url,
            item.domain,
            item.threat,
            item.risk_score if getattr(item, "risk_score", None) is not None else "",
            item.date_added.isoformat() if item.date_added is not None else "",
            item.status,
            item.source,
        ])

    return output.getvalue()
