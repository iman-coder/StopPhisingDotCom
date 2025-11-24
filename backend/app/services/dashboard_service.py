from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any

from app.models import URL
from app.utils.logger import get_logger
from app.utils.threat import normalize_threat

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
        db.query(URL.id, URL.url, URL.domain, URL.threat, URL.date_added, URL.status)
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
            "status": r[5],
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


# Use the shared normalizer from utils.threat


def _build_date_groups(rows):
    # rows: list of tuples (date, threat, count)
    groups = {}
    for d, threat, cnt in rows:
        key = d
        groups.setdefault(key, {"scanned": 0, "suspicious": 0, "malicious": 0, "safe": 0})
        norm = normalize_threat(threat)
        groups[key]["scanned"] += cnt
        if norm in groups[key]:
            groups[key][norm] += cnt
    return groups


def get_time_series_by_day_breakdown(db: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Return list of {'date': 'YYYY-MM-DD', 'scanned': n, 'suspicious': x, 'malicious': y, 'safe': z}
    for the last `days` days.
    """
    date_col = func.date(URL.date_added)
    rows = (
        db.query(date_col.label("d"), URL.threat, func.count(URL.id))
        .filter(URL.date_added != None)
        .group_by(date_col, URL.threat)
        .order_by(desc("d"))
        .limit(days * 10)
        .all()
    )

    # aggregate per date
    grouped = _build_date_groups(rows)

    # produce chronological list for the last `days` (fill missing dates as zeros optional)
    sorted_keys = sorted(grouped.keys())
    # frontend expects key 'day' for daily entries
    series = [{"day": k, **grouped[k]} for k in sorted_keys][-days:]
    logger.debug("daily breakdown series (last %s days): %s", days, series)
    return series


def get_time_series_by_month_breakdown(db: Session, months: int = 12) -> List[Dict[str, Any]]:
    """Return list of {'month': 'YYYY-MM', 'scanned': n, ...} aggregated by month.
    Uses sqlite `strftime` for month formatting if necessary; falls back to truncation for other DBs.
    """
    # determine dialect
    try:
        bind = db.get_bind()
        dialect = bind.dialect.name
    except Exception:
        dialect = "sqlite"

    if dialect == "sqlite":
        month_expr = func.strftime("%Y-%m", URL.date_added)
    else:
        # postgres and others: try to use to_char(date_trunc('month', ...), 'YYYY-MM')
        month_expr = func.to_char(func.date_trunc("month", URL.date_added), "YYYY-MM")

    rows = (
        db.query(month_expr.label("d"), URL.threat, func.count(URL.id))
        .filter(URL.date_added != None)
        .group_by(month_expr, URL.threat)
        .order_by(desc("d"))
        .limit(months * 10)
        .all()
    )

    grouped = _build_date_groups(rows)
    sorted_keys = sorted(grouped.keys())
    series = [{"month": k, **grouped[k]} for k in sorted_keys][-months:]
    logger.debug("monthly breakdown series (last %s months): %s", months, series)
    return series


# --- Compatibility layer: functions expected by routes/dashboard.py --- #

def get_global_metrics_service(db: Session) -> Dict[str, Any]:
    """Return a small summary for the dashboard metrics endpoint."""
    total = get_total_urls(db)
    by_threat_list = get_counts_by_threat(db)
    # iterate the threat counts and normalize each threat label before bucketing
    safe = 0
    suspicious = 0
    malicious = 0

    for entry in by_threat_list:
        raw_threat = entry.get("threat")
        cnt = int(entry.get("count", 0) or 0)
        norm = normalize_threat(raw_threat)
        if norm == "safe":
            safe += cnt
        elif norm == "suspicious":
            suspicious += cnt
        elif norm == "malicious":
            malicious += cnt
        else:
            # Unknown/other threats are not assigned to these buckets; leave them out
            pass

    return {
        "total_urls": total,
        "safe": safe,
        "suspicious": suspicious,
        "malicious": malicious,
    }


def get_risk_distribution_service(db: Session) -> List[Dict[str, Any]]:
    # return a mapping expected by frontend: {safe: n, suspicious: m, malicious: k}
    rows = get_counts_by_threat(db)
    # normalize each threat key and sum into canonical buckets
    safe = 0
    suspicious = 0
    malicious = 0
    for r in rows:
        raw = r.get("threat")
        cnt = int(r.get("count", 0) or 0)
        norm = normalize_threat(raw)
        if norm == "safe":
            safe += cnt
        elif norm == "suspicious":
            suspicious += cnt
        elif norm == "malicious":
            malicious += cnt

    return {"safe": safe, "suspicious": suspicious, "malicious": malicious}


def get_status_distribution_service(db: Session) -> List[Dict[str, Any]]:
    rows = get_counts_by_status(db)
    return {r["status"]: r["count"] for r in rows}


def get_domain_counts_service(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    # Return only the top `limit` domains to keep the chart focused.
    rows = get_top_domains(db, limit=limit)
    # convert list of {domain,count} to mapping {domain: count}
    return {r["domain"]: r["count"] for r in rows}


def get_top_risky_domains_service(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
    return get_top_domains(db, limit=limit)


def get_monthly_activity_service(db: Session):
    return get_time_series_by_month_breakdown(db, months=12)


def get_daily_activity_service(db: Session):
    return get_time_series_by_day_breakdown(db, days=7)


def get_top_risky_urls_service(db: Session, limit: int = 10):
    # reuse recent_urls for now (could be sorted by threat/severity)
    rows = get_recent_urls(db, limit=limit)
    # map threat -> risk for frontend
    out = []
    for r in rows:
        risk = normalize_threat(r.get("threat"))
        out.append({"id": r.get("id"), "url": r.get("url"), "risk": risk})
    return out


def get_recent_urls_service(db: Session, limit: int = 10):
    # frontend expects 'status' field; recent_urls already includes it
    rows = get_recent_urls(db, limit=limit)
    # keep only the fields frontend uses: id, url, status
    return [{"id": r.get("id"), "url": r.get("url"), "status": r.get("status")} for r in rows]


def get_recent_events_service(db: Session, limit: int = 10):
    # produce a lightweight 'events' feed from recent URLs (default limit 10)
    recent = get_recent_urls(db, limit=limit)
    events = []
    for r in recent:
        events.append({
            "id": r["id"],
            "action": "added",
            "url": r["url"],
            "timestamp": r.get("date_added"),
        })
    return events


def search_dashboard_service(db: Session, q: str | None):
    if not q:
        return []
    qlike = f"%{q}%"
    rows = (
        db.query(URL.id, URL.url, URL.domain, URL.threat, URL.status)
        .filter((URL.url.ilike(qlike)) | (URL.domain.ilike(qlike)))
        .limit(50)
        .all()
    )
    result = [
        {"id": r[0], "url": r[1], "domain": r[2], "threat": r[3], "status": r[4]}
        for r in rows
    ]
    return result
