from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal, DATABASE_URL
from app.schemas import URLCreate, URLResponse, URLUpdate
from app.services import url_service
from app.utils.logger import get_logger
from app.utils.auth import get_current_admin_user, get_current_user
from app.schemas import URLListResponse
from app.utils.rate_limit import rate_limit_dep

logger = get_logger(__name__)

router = APIRouter(prefix="/urls", tags=["URLs"])

# Rate limit for search/list: 60 requests per minute per IP/user, burst 10
search_rate_dep = rate_limit_dep("urls:search", limit_per_minute=60, burst=10)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health") # Health test endpoint
def health():
    return {"status": "ok"}


@router.get("/", response_model=URLListResponse, dependencies=[Depends(search_rate_dep)])
def get_all_urls(query: str | None = None, page: int = 1, per_page: int = 25, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Return paginated URLs. Requires authenticated user."""
    return url_service.search_urls(db, q=query, page=page, per_page=per_page)


@router.get("/count")
def get_count(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Return URL count. Requires authenticated user."""
    return {"count": len(url_service.get_all_urls(db))}


@router.post("/", response_model=URLResponse)
def create_url(url: URLCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """Create a new URL. Requires authenticated user."""
    return url_service.create_url(db, url)


@router.put("/{url_id}", response_model=URLResponse)
def update_url(url_id: int, url: URLUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin_user)):
    """Update an existing URL. Requires authenticated user."""
    return url_service.update_url(db, url_id, url)


@router.delete("/{url_id}")
def delete_url(url_id: int, db: Session = Depends(get_db), current_admin=Depends(get_current_admin_user)):
    return url_service.delete_url(db, url_id)


@router.delete("/")
def delete_all(db: Session = Depends(get_db), current_admin=Depends(get_current_admin_user)):
    """Delete all URLs. Protected: admin-only.

    Returns: {"deleted": n}
    """
    try:
        before = len(url_service.get_all_urls(db))
        res = url_service.delete_all_urls(db)
        after = len(url_service.get_all_urls(db))
        logger.info(f"delete_all invoked: before={before} deleted={res.get('deleted')} after={after}")
        return {"deleted": res.get("deleted"), "before": before, "after": after}
    except Exception as e:
        logger.exception("delete_all failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug")
def debug_info(db: Session = Depends(get_db), current_admin=Depends(get_current_admin_user)):
    try:
        rows = url_service.get_all_urls(db)
        count = len(rows)
        sample = []
        for r in rows[:10]:
            sample.append({
                "id": r.id,
                "url": r.url,
                "threat": r.threat,
                "date_added": r.date_added.isoformat() if r.date_added is not None else None,
                "status": r.status,
            })

        db_file = None
        if DATABASE_URL and DATABASE_URL.startswith("sqlite"):
            db_file = DATABASE_URL.replace("sqlite:///", "")

        return {"database_url": DATABASE_URL, "db_file": db_file, "count": count, "sample": sample}
    except Exception as e:
        logger.exception("debug_info failed")
        raise HTTPException(status_code=500, detail=str(e))
