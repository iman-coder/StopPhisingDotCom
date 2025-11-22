from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.schemas import URLCreate, URLResponse, URLUpdate
from app.services import url_service

router = APIRouter(prefix="/urls", tags=["URLs"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health") # Health test endpoint
def health():
    return {"status": "ok"}


@router.get("/", response_model=list[URLResponse])
def get_urls(db: Session = Depends(get_db)):
    return url_service.get_all_urls(db)


@router.post("/", response_model=URLResponse)
def create_url(url: URLCreate, db: Session = Depends(get_db)):
    return url_service.create_url(db, url)


@router.put("/{url_id}", response_model=URLResponse)
def update_url(url_id: int, url: URLUpdate, db: Session = Depends(get_db)):
    return url_service.update_url(db, url_id, url)


@router.delete("/{url_id}")
def delete_url(url_id: int, db: Session = Depends(get_db)):
    return url_service.delete_url(db, url_id)
