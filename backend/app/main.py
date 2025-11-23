from fastapi import FastAPI
from app.routes import urls  # we’ll add dashboard later
from app.routes import csv as csv_routes
from app.routes import dashboard
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import configure_logging, get_logger

app = FastAPI(title="URL Dashboard API")

# configure logging early
configure_logging()
logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        import time

        start = time.time()
        logger.info(f"incoming request: {request.method} {request.url.path}")
        response = await call_next(request)
        duration = (time.time() - start) * 1000
        logger.info(f"completed {request.method} {request.url.path} -> {response.status_code} in {duration:.2f}ms")
        return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # should change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

app.include_router(urls.router)
app.include_router(csv_routes.router)
app.include_router(dashboard.router)