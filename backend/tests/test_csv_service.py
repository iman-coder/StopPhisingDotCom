from app.utils import database
from app.services import csv_service
from app.models import URL


def setup_module(module):
    database.Base.metadata.create_all(bind=database.engine)


def teardown_module(module):
    database.Base.metadata.drop_all(bind=database.engine)


def test_import_and_export_csv():
    db = database.SessionLocal()
    try:
        # clean
        db.query(URL).delete()
        db.commit()

        csv_content = "url,domain,threat,status,source\nhttps://a.test,a.test,high,new,import\n,missing,low,new,import\nhttps://a.test,a.test,high,new,import\n"

        res = csv_service.import_csv(csv_content, db)
        assert res["inserted"] == 1
        assert res["skipped"] >= 1

        out = csv_service.export_csv(db)
        assert "https://a.test" in out
        # header present
        assert out.splitlines()[0].startswith("id,url,domain")

    finally:
        db.close()
