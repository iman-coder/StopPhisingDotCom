from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal
from app.utils import security
from app.models import User
import logging

logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(security.oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = security.decode_access_token(token)
    except Exception as e:
        # Log the decode error with masked token start to aid debugging in dev
        try:
            masked = (token[:10] + '...') if token and len(token) > 10 else token
        except Exception:
            masked = '<unavailable>'
        logger.exception("Failed to decode access token (start=%s): %s", masked, e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    username: str | None = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return current_user
