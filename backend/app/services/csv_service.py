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

    for row in reader:
        url_value = row.get("url")
        if not url_value:
            skipped.append(row)
            continue

        # Avoid duplicate URLs
        existing = db.query(URL).filter(URL.url == url_value).first()
        if existing:
            skipped.append(row)
            continue

        new_url = URL(
            url=row.get("url"),
            domain=row.get("domain"),
            threat=row.get("threat"),
            status=row.get("status"),
            source=row.get("source"),
        )

        db.add(new_url)
        created_count += 1

    db.commit()

    return {
        "inserted": created_count,
        "skipped": len(skipped)
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
            item.date_added,
            item.status,
            item.source,
        ])

    return output.getvalue()
