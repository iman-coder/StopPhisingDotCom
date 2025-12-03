from sqlalchemy.orm import Session
from app.models import URL
from app.schemas import URLCreate, URLUpdate
from fastapi import HTTPException
from app.utils.threat import normalize_threat
from app.utils import cache
from sqlalchemy import or_, func, cast
from sqlalchemy.types import String


def get_all_urls(db: Session):
    # Return rows ordered by `date_added` descending so newest items appear first.
    # When `date_added` is NULL, SQLAlchemy will place them last by default.
    return db.query(URL).order_by(URL.date_added.desc()).all()


def search_urls(db: Session, q: str | None = None, page: int = 1, per_page: int = 25, use_cache: bool = True):
    """Search URLs with pagination. Returns dict {items, total, page, per_page}.

    Uses a simple LIKE-based search across several fields. Caches results in Redis
    when `use_cache` is True and `q` is non-empty.
    """
    key = None
    if use_cache and q:
        key = f"search:{q}:{page}:{per_page}"
        cached = cache.cache_get(key)
        if cached is not None:
            return cached

    query = db.query(URL)
    if q:
        term = f"%{q.lower()}%"
        # case-insensitive matches across text fields and id
        query = query.filter(
            or_(
                func.lower(URL.url).like(term),
                func.lower(URL.domain).like(term),
                func.lower(URL.threat).like(term),
                func.lower(URL.status).like(term),
                func.lower(URL.source).like(term),
                cast(URL.id, String).like(term),
            )
        )

    total = query.count()
    items = query.order_by(URL.date_added.desc()).offset((page - 1) * per_page).limit(per_page).all()

    result = {"items": items, "total": total, "page": page, "per_page": per_page}
    if key:
        # cache short-lived for responsiveness; failures are ignored inside cache module
        cache.cache_set(key, result, ttl=30)
    return result


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
