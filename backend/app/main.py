from fastapi import FastAPI
from contextlib import asynccontextmanager
# Route imports moved below app creation to avoid import-time circular issues
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import configure_logging, get_logger
import os
from dotenv import load_dotenv

# Load environment files to ensure default env vars (SINGLE_ADMIN_* etc.)
# are available when running the app locally or in tests. Historically the
# repository used a top-level `.env`; some workflows use an external `env`
# (no dot) file. Load both when present so local development using `.env`
# continues to work while allowing an external `env` file in deployments.
repo_root = os.path.join(os.path.dirname(__file__), '..', '..')
env_path = os.path.join(repo_root, 'env')
dot_env_path = os.path.join(repo_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
if os.path.exists(dot_env_path):
    load_dotenv(dot_env_path)
from app.utils.database import engine, SessionLocal, Base
import sys
from app.utils import security

# configure logging early
configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Lifespan handler replaces deprecated on_event startup handlers.
    # Create tables and seed a default admin user before the app handles requests.
    try:
        # import models module without binding the top-level `app` name in this
        # module's globals to avoid shadowing the FastAPI `app` variable.
        from importlib import import_module
        import_module("app.models")
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            from app.models import User, URL

            admin_name = os.getenv("SINGLE_ADMIN_USERNAME", "admin")
            admin_pw = os.getenv("SINGLE_ADMIN_PASSWORD", "changeme")

            existing = db.query(User).filter(User.username == admin_name).first()
            if not existing:
                hashed = security.get_password_hash(admin_pw)
                user = User(username=admin_name, hashed_password=hashed, is_admin=True)
                db.add(user)
                db.commit()
                logger.info(f"Created default admin user '{admin_name}' on startup")
            else:
                # If an admin already exists but the stored password does not match
                # the current `SINGLE_ADMIN_PASSWORD` env var, update it. This
                # makes test runs deterministic when environment vars differ.
                try:
                    if not security.verify_password(admin_pw, existing.hashed_password):
                        existing.hashed_password = security.get_password_hash(admin_pw)
                        db.add(existing)
                        db.commit()
                        logger.info(f"Updated password for existing admin user '{admin_name}' to match env")
                except Exception:
                    logger.exception("Failed to verify/update existing admin password")

            # Seed a deterministic non-admin user from env for development/tests.
            nonadmin_name = os.getenv("SINGLE_NONADMIN_USERNAME", "user")
            nonadmin_pw = os.getenv("SINGLE_NONADMIN_PASSWORD", "changeme")
            try:
                non_existing = db.query(User).filter(User.username == nonadmin_name).first()
                if not non_existing:
                    hashed = security.get_password_hash(nonadmin_pw)
                    user = User(username=nonadmin_name, hashed_password=hashed, is_admin=False)
                    db.add(user)
                    db.commit()
                    logger.info(f"Created default non-admin user '{nonadmin_name}' on startup")
                else:
                    # If the existing user is an admin, skip changing their role
                    if getattr(non_existing, "is_admin", False):
                        logger.info(f"Existing user '{nonadmin_name}' is admin; skipping non-admin seed")
                    else:
                        try:
                            if not security.verify_password(nonadmin_pw, non_existing.hashed_password):
                                non_existing.hashed_password = security.get_password_hash(nonadmin_pw)
                                db.add(non_existing)
                                db.commit()
                                logger.info(f"Updated password for existing non-admin user '{nonadmin_name}' to match env")
                        except Exception:
                            db.rollback()
            except Exception:
                logger.exception("Failed to create/update non-admin seed user")

            # Only clear the urls table for ephemeral/test DBs to avoid deleting
            # production data. Detect testing by presence of pytest or by a
            # memory-based DATABASE_URL.
            db_url = os.getenv("DATABASE_URL", "")
            is_test_db = ("pytest" in sys.modules) or ("memory" in db_url)
            if is_test_db:
                try:
                    deleted = db.query(URL).delete()
                    if deleted:
                        logger.info(f"Cleared {deleted} rows from urls table on startup (test mode)")
                    db.commit()
                except Exception:
                    db.rollback()
        finally:
            db.close()
    except Exception:
        logger.exception("Lifespan startup: failed to create tables or seed admin")

    yield

    # Place for shutdown actions if needed in future


# create app with lifespan handler
app = FastAPI(title="URL Dashboard API", lifespan=lifespan)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time

        start = time.time()
        logger.info(f"incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info(f"completed {request.method} {request.url.path} -> {response.status_code} in {duration:.2f}ms")
        return response


# Configure CORS origins via environment for flexible dev setups.
# Set FRONTEND_ORIGINS='http://localhost:5173,http://127.0.0.1:5173' or '*' for all origins (not recommended for prod).
origins_env = os.getenv("FRONTEND_ORIGINS")
if origins_env:
    if origins_env.strip() == "*":
        allow_origins = ["*"]
        allow_credentials = False
    else:
        allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
        allow_credentials = True
else:
    allow_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
    allow_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Import routers after `app` exists to prevent circular import problems
from app.routes import urls  # we’ll add dashboard later
from app.routes import csv as csv_routes
from app.routes import dashboard
from app.routes import auth as auth_routes

app.include_router(urls.router)
app.include_router(csv_routes.router)
app.include_router(dashboard.router)
app.include_router(auth_routes.router)

# Import-time fallback: ensure tables exist before TestClient instantiates app.
# Lifespan will also run on server startup, but some test runners create the
# TestClient immediately and expect DB tables to already exist.
try:
    from importlib import import_module
    import_module("app.models")
    Base.metadata.create_all(bind=engine)
    # Attempt a lightweight import-time admin seed so tests or tools that
    # instantiate the app without running the full lifespan still get a
    # usable admin user derived from env vars (including values loaded from
    # `.env.example` above). If this fails, the lifespan handler will seed.
    try:
        from app.models import User
        from app.utils import security as _security
        _db = SessionLocal()
        try:
            admin_name = os.getenv("SINGLE_ADMIN_USERNAME", "admin")
            admin_pw = os.getenv("SINGLE_ADMIN_PASSWORD", "changeme")
            _existing = _db.query(User).filter(User.username == admin_name).first()
            if not _existing:
                _db.add(User(username=admin_name, hashed_password=_security.get_password_hash(admin_pw), is_admin=True))
                _db.commit()
                # Import-time non-admin seed
                nonadmin_name = os.getenv("SINGLE_NONADMIN_USERNAME", "user")
                nonadmin_pw = os.getenv("SINGLE_NONADMIN_PASSWORD", "changeme")
                try:
                    _non = _db.query(User).filter(User.username == nonadmin_name).first()
                    if not _non:
                        _db.add(User(username=nonadmin_name, hashed_password=_security.get_password_hash(nonadmin_pw), is_admin=False))
                        _db.commit()
                except Exception:
                    # Non-fatal; import-time seed is best-effort
                    pass
        finally:
            _db.close()
    except Exception:
        logger.debug("Import-time admin seed skipped; lifespan will handle it")
except Exception:
    logger.debug("Import-time create_all skipped or failed; lifespan will handle it")