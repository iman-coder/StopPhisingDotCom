# URL Management & Dashboard Project

This project is a web application for monitoring and managing URLs. It consists of a Vue 3 frontend and a Python backend (FastAPI). The frontend displays dashboards and allows URL CRUD operations, while the backend exposes APIs to provide data and handle requests.

"""
StopPhisingDotCom — URL Dashboard & Manager

Lightweight web app for importing, scanning and monitoring URLs. Includes a FastAPI backend and a Vue 3 frontend with dashboards and CRUD for URLs.

This README gives the steps to get the project running locally (Windows PowerShell examples), where to find key files, and common troubleshooting tips.
"""

---

## Quickstart (recommended)

1) Start the backend (from the `backend` folder):

```powershell
# from repository root
cd .\backend
# create & activate venv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# run the server
uvicorn app.main:app --reload
```

2) Start the frontend (from the `frontend` folder):

```powershell
cd ..\frontend    # or `phishing-frontend` if that's your folder
npm install
npm run dev
```

Open `http://localhost:5173` (Vite default) for the frontend and `http://127.0.0.1:8000/docs` to view the backend OpenAPI docs.

---

## Project layout (high-level)

- `backend/` — FastAPI app in `backend/app/` with routes, services, and utils.
- `frontend/` (or `phishing-frontend/`) — Vue 3 app (Vite) in `frontend/src/`.
- utility scripts in the repo root for data preparation (CSV/JSON helpers).

Key backend files:
- `backend/app/main.py` — FastAPI app entrypoint
- `backend/app/models.py` — SQLAlchemy models
- `backend/app/routes/urls.py` — URL CRUD and CSV import/export
- `backend/app/routes/dashboard.py` — dashboard endpoints
- `backend/app/services/*` — business logic (CSV import, dashboard aggregation)

Key frontend files:
- `frontend/src/services/*` — API client modules (`urlService.js`, `dashboardService.js`)
- `frontend/src/components/*` — UI components (forms, tables, charts)

# StopPhishingDotCom — URL Dashboard & Manager

Lightweight web app for importing, classifying and monitoring URLs. The project contains a FastAPI backend and a Vue 3 frontend (Vite) that provides dashboards and URL CRUD operations.

This README shows how to run the app locally (PowerShell examples), how to use Docker Compose for a reproducible dev environment, and common troubleshooting tips.

---

**Quick Start (Docker Compose)**

- Create a local `.env` from the provided example and set strong credentials (do not commit `.env`):

```powershell
Copy-Item .\.env.example .\.env
notepad .\.env
```

- Start the stack (backend, frontend, redis, Postgres):

```powershell
# from repository root
docker-compose up -d --build
```

- Watch backend logs while it starts (helpful for DB/migration messages):

```powershell
docker-compose logs -f backend
```

Open the frontend at `http://localhost:5173` and the API docs at `http://127.0.0.1:8000/docs`.

---

**Development (Backend)**

- Create and activate a venv, install dependencies, run the server locally:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Run tests:

```powershell
cd backend
pytest -q
```

Notes:
- The backend reads `DATABASE_URL` from the environment. When using Docker Compose, the compose file builds the `DATABASE_URL` from top-level variables in `./.env`.
- `backend/.env` is kept for local, backend-only overrides (e.g. `SECRET_KEY`, local SQLite path). Avoid duplicating DB credentials across both files.

---

**Development (Frontend)**

```powershell
cd frontend
npm install
npm run dev
```

The frontend uses relative API paths so Vite can proxy to the backend during development. If you change the backend host/port, update the Vite proxy in `vite.config.js` or the base URL in `frontend/src/services/*.js`.

---

**Database & Migrations**

- With Compose you normally do NOT need Postgres exposed on the host. If you need host access, use a different host port (e.g. `5433:5432`) in `docker-compose.yml`.
- Apply migrations after the DB is ready:

```powershell
# run migrations from the host using the backend container
docker-compose exec backend sh -c "alembic upgrade head"
```

Or run `alembic` locally against your `DATABASE_URL`.

Important: Compose's `depends_on` ensures the DB container starts, but does not wait for readiness. If your backend fails on startup due to DB not accepting connections, add a small wait-for script or use a healthcheck for Postgres.

---

**Environment files and secrets**

- Use the top-level `./.env` for service-level variables (Postgres, Redis). Keep `backend/.env` for backend-only local overrides.
- `./.env.example` contains placeholders — copy it to `./.env` and fill with secure values. `./.env` is ignored by Git by default.

Example (local `./.env`):

```env
POSTGRES_USER=stopphish
POSTGRES_PASSWORD=ReplaceThisWithAStrongPassword
POSTGRES_DB=stopphishing
POSTGRES_PORT=5432
REDIS_URL=redis://redis:6379/0
```

---

**API Highlights**

- `GET /dashboard/metrics` — high-level counts: `total_urls`, `safe`, `suspicious`, `malicious`.
- `GET /dashboard/risk-distribution` — normalized breakdown for charts.
- `GET /dashboard/domains?limit=10` — top domain counts.
- `GET /urls` — list URLs.
- `POST /urls/import` — CSV import (`url`, optional `domain`, `threat`, `status`, `source`).

Use `http://127.0.0.1:8000/docs` for the full OpenAPI schema and interactive testing.

---

**Troubleshooting**

- Port 5432 already in use:
  - Option 1 (recommended): remove the `ports:` mapping for the `db` service in `docker-compose.yml` so Postgres is accessible only to containers.
  - Option 2: change host mapping to `5433:5432` in `docker-compose.yml`.

- Backend returns HTTP 500 on endpoints:
  - Check backend logs: `docker-compose logs --tail=200 backend` and `docker-compose logs -f backend` while re-triggering the request.
  - Inspect `GET /urls/debug` (if present) to see the `DATABASE_URL` used by the running container.

- Dashboard counts incorrect:
  - Threats are normalized at import and aggregation; inspect `GET /dashboard/risk-distribution` for the normalized buckets.

---

**Contributing & Next Steps**

- To add DB health checks or a wait-for script I can update `docker-compose.yml` and the backend entrypoint so the app only starts after the DB accepts connections.
- To avoid secrets in repos for production, use Docker secrets or your platform's secret store.

If you want, I can now:
- create a local `./.env` from `.env.example` and bring the stack up, run migrations and test the dashboard endpoint, or
- add a `wait-for-db` script and a Postgres healthcheck to `docker-compose.yml`.

---

License: MIT-style (add `LICENSE` file to publish a formal license).

Happy hacking! If you'd like changes to the README wording or more examples (like `vite.config.js` proxy), tell me which section to expand.
