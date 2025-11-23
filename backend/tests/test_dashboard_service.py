from app.utils import database
from app.services import dashboard_service
from app.models import URL
from datetime import datetime, timedelta


def setup_module(module):
    database.Base.metadata.create_all(bind=database.engine)


def teardown_module(module):
    database.Base.metadata.drop_all(bind=database.engine)


def _seed_urls(db):
    db.query(URL).delete()
    now = datetime.utcnow()
    rows = [
        URL(url=f"https://site{i}.test", domain=f"site{i}.test", threat="high" if i % 2 == 0 else "low", status="new", source="seed", date_added=now - timedelta(days=i))
        for i in range(6)
    ]
    db.add_all(rows)
    db.commit()


def test_dashboard_aggregations():
    db = database.SessionLocal()
    try:
        _seed_urls(db)

        total = dashboard_service.get_total_urls(db)
        assert total >= 6

        threats = dashboard_service.get_counts_by_threat(db)
        assert any(d["threat"] in ("high", "low") for d in threats)

        statuses = dashboard_service.get_counts_by_status(db)
        assert isinstance(statuses, list)

        top = dashboard_service.get_top_domains(db, limit=3)
        assert len(top) <= 3

        recent = dashboard_service.get_recent_urls(db, limit=3)
        assert len(recent) == 3

        series = dashboard_service.get_time_series_by_day(db, days=7)
        assert isinstance(series, list)

        # compatibility wrappers
        gm = dashboard_service.get_global_metrics_service(db)
        assert "total" in gm

    finally:
        db.close()
