# app/services/csv_service.py

import csv
from io import StringIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import URL
from app.schemas import URLCreate
from app.utils.logger import get_logger
from app.utils.threat import normalize_threat

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
        raw_threat = norm_row.get("threat")
        normalized = normalize_threat(raw_threat)
        new_url = URL(
            url=url_value,
            domain=norm_row.get("domain") or norm_row.get("host"),
            threat=normalized,
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

    # CSV header
    writer.writerow(["id", "url", "domain", "threat", "date_added", "status", "source"])

    # CSV rows
    for item in urls:
        writer.writerow([
            item.id,
            item.url,
            item.domain,
            item.threat,
            item.date_added.isoformat() if item.date_added is not None else "",
            item.status,
            item.source,
        ])

    return output.getvalue()
