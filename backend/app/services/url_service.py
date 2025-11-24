from sqlalchemy.orm import Session
from app.models import URL
from app.schemas import URLCreate, URLUpdate
from fastapi import HTTPException
from app.utils.threat import normalize_threat


def get_all_urls(db: Session):
    return db.query(URL).all()


def create_url(db: Session, url_data: URLCreate):
    # normalize threat field so stored values are canonical
    data = url_data.dict()
    if "threat" in data:
        data["threat"] = normalize_threat(data.get("threat"))
    new_url = URL(**data)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)
    return new_url


def update_url(db: Session, url_id: int, url_data: URLUpdate):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Only update fields that were explicitly provided and are not None
    updates = url_data.dict(exclude_unset=True, exclude_none=True)
    # normalize threat if provided
    if "threat" in updates:
        updates["threat"] = normalize_threat(updates.get("threat"))
    for key, value in updates.items():
        setattr(db_url, key, value)

    db.commit()
    db.refresh(db_url)
    return db_url


def delete_url(db: Session, url_id: int):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(status_code=404, detail="URL not found")

    db.delete(db_url)
    db.commit()
    return {"detail": "URL deleted"}


def delete_all_urls(db: Session):
    """Delete all URL records from the database.

    Returns a dict with the number of rows deleted.
    """
    # Use Query.delete() for efficiency; returns number of rows deleted
    deleted = db.query(URL).delete()
    db.commit()
    return {"deleted": int(deleted)}
