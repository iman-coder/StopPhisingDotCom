# app/services/csv_service.py

import csv
from io import StringIO
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models import URL
from app.schemas import URLCreate


# -------- CSV IMPORT -------- #

def import_csv(file_content: str, db: Session):
    reader = csv.DictReader(StringIO(file_content))
    created_count = 0
    skipped = []

    # preload existing URLs from DB to avoid unique constraint violations
    existing_urls = set([r[0] for r in db.query(URL.url).all()]) if db.query(URL).count() > 0 else set()
    seen = set()

    for row in reader:
        url_value = row.get("url")
        if not url_value:
            skipped.append(row)
            continue

        # Avoid duplicate URLs (both in DB and already seen in this import)
        if url_value in existing_urls or url_value in seen:
            skipped.append(row)
            continue

        new_url = URL(
            url=url_value,
            domain=row.get("domain"),
            threat=row.get("threat"),
            status=row.get("status"),
            source=row.get("source"),
        )

        db.add(new_url)
        created_count += 1
        seen.add(url_value)

    db.commit()

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
