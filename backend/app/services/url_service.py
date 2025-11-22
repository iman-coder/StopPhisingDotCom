from sqlalchemy.orm import Session
from app.models import URL
from app.schemas import URLCreate, URLUpdate
from fastapi import HTTPException


def get_all_urls(db: Session):
    return db.query(URL).all()


def create_url(db: Session, url_data: URLCreate):
    new_url = URL(**url_data.dict())
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
