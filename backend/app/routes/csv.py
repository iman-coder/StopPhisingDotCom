from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.services.csv_service import export_csv, import_csv

router = APIRouter(prefix="/urls", tags=["CSV"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export")
def export_csv_route(db: Session = Depends(get_db)):
    csv_bytes = export_csv(db)

    return StreamingResponse(
        iter([csv_bytes]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=urls.csv"
        }
    )


@router.post("/import")
def import_csv_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    inserted = import_csv(db)

    return {"detail": f"{inserted} rows imported"}