from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any

from app.models import URL
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_total_urls(db: Session) -> int:
    """Return total number of URLs."""
    total = db.query(func.count(URL.id)).scalar() or 0
    logger.debug("total urls: %s", total)
    return total


def get_counts_by_threat(db: Session) -> List[Dict[str, Any]]:
    """Return counts grouped by `threat` value."""
    rows = db.query(URL.threat, func.count(URL.id)).group_by(URL.threat).all()
    result = [{"threat": r[0] or "unknown", "count": r[1]} for r in rows]
    logger.debug("counts by threat: %s", result)
    return result


def get_counts_by_status(db: Session) -> List[Dict[str, Any]]:
    """Return counts grouped by `status` value."""
    rows = db.query(URL.status, func.count(URL.id)).group_by(URL.status).all()
    result = [{"status": r[0] or "unknown", "count": r[1]} for r in rows]
    logger.debug("counts by status: %s", result)
    return result


def get_top_domains(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Return top domains by count."""
    rows = (
        db.query(URL.domain, func.count(URL.id).label("c"))
        .group_by(URL.domain)
        .order_by(desc("c"))
        .limit(limit)
        .all()
    )
    result = [{"domain": r[0] or "(none)", "count": r[1]} for r in rows]
    logger.debug("top domains: %s", result)
    return result


def get_recent_urls(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    """Return most recently added URLs with basic fields."""
    rows = (
        db.query(URL.id, URL.url, URL.domain, URL.threat, URL.date_added)
        .order_by(desc(URL.date_added))
        .limit(limit)
        .all()
    )
    result = [
        {
            "id": r[0],
            "url": r[1],
            "domain": r[2],
            "threat": r[3],
            "date_added": r[4].isoformat() if r[4] is not None else None,
        }
        for r in rows
    ]
    logger.debug("recent urls: %s", result)
    return result


def get_time_series_by_day(db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Return a time-series of counts per day for the last `days` days.

    The output is a list of dicts: {"date": "YYYY-MM-DD", "count": n}
    """
    # Use func.date to be portable between sqlite and postgres
    date_col = func.date(URL.date_added)
    rows = (
        db.query(date_col.label("d"), func.count(URL.id))
        .filter(URL.date_added != None)
        .group_by(date_col)
        .order_by(desc("d"))
        .limit(days)
        .all()
    )
    # rows are in descending date order; convert and reverse to chronological
    series = [{"date": r[0], "count": r[1]} for r in reversed(rows)]
    logger.debug("time series (last %s days): %s", days, series)
    return series


# --- Compatibility layer: functions expected by routes/dashboard.py --- #

def get_global_metrics_service(db: Session) -> Dict[str, Any]:
    """Return a small summary for the dashboard metrics endpoint."""
    total = get_total_urls(db)
    by_threat = get_counts_by_threat(db)
    by_status = get_counts_by_status(db)
    return {"total": total, "by_threat": by_threat, "by_status": by_status}


def get_risk_distribution_service(db: Session) -> List[Dict[str, Any]]:
    return get_counts_by_threat(db)


def get_status_distribution_service(db: Session) -> List[Dict[str, Any]]:
    return get_counts_by_status(db)


def get_domain_counts_service(db: Session) -> List[Dict[str, Any]]:
    return get_top_domains(db, limit=100)


def get_top_risky_domains_service(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    return get_top_domains(db, limit=limit)


def get_monthly_activity_service(db: Session):
    # approximate: return last 30 days as monthly summary (could aggregate by month)
    return get_time_series_by_day(db, days=30)


def get_daily_activity_service(db: Session):
    return get_time_series_by_day(db, days=7)


def get_top_risky_urls_service(db: Session, limit: int = 10):
    # reuse recent_urls for now (could be sorted by threat/severity)
    return get_recent_urls(db, limit=limit)


def get_recent_urls_service(db: Session, limit: int = 10):
    return get_recent_urls(db, limit=limit)


def get_recent_events_service(db: Session, limit: int = 20):
    # events are not implemented; fallback to recent urls as proxy
    return get_recent_urls(db, limit=limit)


def search_dashboard_service(db: Session, q: str | None):
    if not q:
        return []
    qlike = f"%{q}%"
    rows = (
        db.query(URL.id, URL.url, URL.domain, URL.threat)
        .filter((URL.url.ilike(qlike)) | (URL.domain.ilike(qlike)))
        .limit(50)
        .all()
    )
    result = [{"id": r[0], "url": r[1], "domain": r[2], "threat": r[3]} for r in rows]
    return result
