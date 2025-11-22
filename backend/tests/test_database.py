from app.utils import database
from app.models import URL
from sqlalchemy import text


def test_engine_connect():
    # simple connect and SELECT 1
    conn = database.engine.connect()
    try:
        res = conn.execute(text("SELECT 1")).scalar()
    finally:
        conn.close()
    assert res == 1


def test_create_and_query_url():
    # create tables (idempotent), insert a URL, query it, then clean up
    database.Base.metadata.create_all(bind=database.engine)

    session = database.SessionLocal()
    try:
        # ensure a clean state for this test key
        session.query(URL).filter(URL.url == "https://unit.test").delete()
        session.commit()

        u = URL(url="https://unit.test", domain="unit.test", threat="none", status="new", source="test")
        session.add(u)
        session.commit()

        found = session.query(URL).filter(URL.url == "https://unit.test").first()
        assert found is not None
        assert found.domain == "unit.test"

        # cleanup the inserted row
        session.delete(found)
        session.commit()
    finally:
        session.close()

    # drop tables created for the test
    database.Base.metadata.drop_all(bind=database.engine)
