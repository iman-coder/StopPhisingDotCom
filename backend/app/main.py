from fastapi import FastAPI
from app.routes import urls  # we’ll add dashboard later
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="URL Dashboard API")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # should change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(urls.router)
# app.include_router(dashboard.router)  # to be added later