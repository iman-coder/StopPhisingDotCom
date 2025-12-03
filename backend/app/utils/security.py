from passlib.context import CryptContext
from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import os
import logging

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
# Default to 60 minutes if env var is not provided or invalid
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except (TypeError, ValueError):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Use PBKDF2 (pure-Python via hashlib) to avoid platform-specific bcrypt wheel issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash.

    For PBKDF2 we don't need to truncate; just ensure the input is a string.
    """
    try:
        norm = _normalize_password(plain_password)
        return pwd_context.verify(norm, hashed_password)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Hash a password using the configured scheme."""
    norm = _normalize_password(password)
    return pwd_context.hash(norm)


def _normalize_password(password: str) -> str:
    """Ensure the password is a string for hashing/verification."""
    if not isinstance(password, str):
        password = str(password)
    return password


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    now = datetime.utcnow()
    expire = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    # Use integer POSIX timestamps for 'iat' and 'exp' for maximum compatibility
    to_encode.update({"iat": int(now.timestamp()), "exp": int(expire.timestamp())})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except Exception:
        # If encoding fails, log and re-raise to preserve behavior
        logger.exception("failed to encode access token")
        raise
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    try:
        # python-jose jwt.decode doesn't accept a `leeway` kwarg on some versions.
        # Decode without verifying the exp claim, then manually enforce exp with
        # a small leeway to tolerate minor clock skew.
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
        exp = payload.get("exp")
        if exp is None:
            raise JWTError("token missing exp claim")
        now = int(datetime.utcnow().timestamp())
        leeway = 5
        if now > int(exp) + leeway:
            # mirror the exception type used elsewhere for expired tokens
            raise ExpiredSignatureError("Signature has expired.")
        return payload
    except JWTError as e:
        # Re-raise after logging to aid debugging during development
        logger.debug("token decode failed", exc_info=e)
        raise e
