from fastapi import APIRouter, Query, Depends
from typing import Optional
from app.services import dashboard_service
from app.utils.database import SessionLocal
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 1. Global Metrics
@router.get("/metrics")
def get_global_metrics(db: Session = Depends(get_db)):
    return dashboard_service.get_global_metrics_service(db)


# 2. Risk / Status distribution
@router.get("/risk-distribution")
def risk_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_risk_distribution_service(db)


@router.get("/status-distribution")
def status_distribution(db: Session = Depends(get_db)):
    return dashboard_service.get_status_distribution_service(db)


# 3. Domain analytics
@router.get("/domains")
def domain_counts(limit: int = 10, db: Session = Depends(get_db)):
    """Return domain counts limited to the top `limit` domains (default 10)."""
    return dashboard_service.get_domain_counts_service(db, limit)


@router.get("/domains/top")
def top_risky_domains(limit: int = 10, db: Session = Depends(get_db)):
    return dashboard_service.get_top_risky_domains_service(db, limit)


# 4. Time series
@router.get("/activity/monthly")
def monthly_activity(db: Session = Depends(get_db)):
    return dashboard_service.get_monthly_activity_service(db)


@router.get("/activity/daily")
def daily_activity(db: Session = Depends(get_db)):
    return dashboard_service.get_daily_activity_service(db)


# 5. Top Lists
@router.get("/urls/top")
def top_risky_urls(limit: int = 10, db: Session = Depends(get_db)):
    return dashboard_service.get_top_risky_urls_service(db, limit)


@router.get("/urls/recent")
def recent_urls(limit: int = 10, db: Session = Depends(get_db)):
    return dashboard_service.get_recent_urls_service(db, limit)


# 6. Activity feed
@router.get("/events")
def recent_events(limit: int = 10, db: Session = Depends(get_db)):
    """Return recent events (default limit 10)."""
    return dashboard_service.get_recent_events_service(db, limit)


# 7. Search
@router.get("/search")
def search(q: Optional[str] = Query(None, alias="q"), db: Session = Depends(get_db)):
    return dashboard_service.search_dashboard_service(db, q)
