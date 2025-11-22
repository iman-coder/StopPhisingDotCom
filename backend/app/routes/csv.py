from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.services.csv_service import export_csv, import_csv
import io

router = APIRouter(prefix="/urls", tags=["CSV"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export")
def export_csv_route(db: Session = Depends(get_db)):
    csv_str = export_csv(db)

    return StreamingResponse(
        io.BytesIO(csv_str.encode("utf-8")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urls.csv"},
    )


@router.post("/import")
async def import_csv_route(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    # read file contents from UploadFile
    content_bytes = await file.read()
    try:
        content = content_bytes.decode("utf-8")
    except Exception:
        # fallback to latin-1 if utf-8 fails
        content = content_bytes.decode("latin-1")

    result = import_csv(content, db)

    return result