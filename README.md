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
- `frontend/src/views/*` — top-level views (Dashboard, URLs)

---

## Environment & configuration

- Backend reads `DATABASE_URL` from environment (defaults to a local SQLite file if unspecified).
- Common env vars (create a `.env` file in `backend/`):

```
DATABASE_URL=sqlite:///./urls.db
LOG_FILE=./logs/app.log
SECRET_KEY=changeme
```

Load `.env` via your shell or use tools (for development with `uvicorn --reload` the project may load `.env` automatically if configured).

---

## Useful commands

Backend (from `backend/`):

```powershell
# install deps
pip install -r requirements.txt

# run unit tests
pytest -q

# run server
uvicorn app.main:app --reload

# quick API checks
curl http://127.0.0.1:8000/dashboard/metrics
curl http://127.0.0.1:8000/urls | Out-String -Width 4096
```

Frontend (from `frontend/` or `phishing-frontend/`):

```powershell
npm install
npm run dev
npm run build    # production build
```

Notes:
- The frontend uses relative API paths so Vite can proxy requests to the backend during development. If you change the backend host/port, update Vite proxy in `vite.config.js` or set the API base in `frontend/src/services/*.js`.

---

## API highlights

- `GET /dashboard/metrics` — summary counts (`total_urls`, `safe`, `suspicious`, `malicious`).
- `GET /dashboard/risk-distribution` — mapping for charting risk buckets.
- `GET /dashboard/domains?limit=10` — domain counts (top N domains).
- `GET /urls` — list URLs
- `POST /urls/import` — multipart upload CSV to import URLs (key columns: `url`, optional `domain`, `threat`, `status`, `source`).

Open `http://127.0.0.1:8000/docs` for the full OpenAPI listing and interactive testing.

---

## Troubleshooting notes

- Counts not matching in the dashboard?
  - The backend normalizes freeform `threat` strings (using `backend/app/utils/threat.py`). If many rows have empty or unknown threat labels they may be bucketed as `unknown` (or `suspicious` depending on configuration). Check raw rows:

    ```powershell
    curl http://127.0.0.1:8000/urls | Out-String -Width 4096
    ```

  - Also check `GET /dashboard/risk-distribution` to see the normalized breakdown the frontend uses.

- CSV import not adding rows?
  - Server logs show `POST /urls/import` processing and summary. Check `backend/app/services/csv_service.py` for header/delimiter heuristics.

- Frontend shows only one row while backend `curl` shows many?
  - Ensure the frontend dev server is proxying `/urls` to `127.0.0.1:8000`. Check `vite.config.js` and verify the frontend `urlService` uses a relative path (e.g. `const API = "/urls/"`).

---

## Developer notes

- To change how threat strings are normalized, edit `backend/app/utils/threat.py` (used by create/update/import and dashboard aggregation).
- To adjust how many domains appear in the domain chart, call `GET /dashboard/domains?limit=10` (backend default is 10).
- To run a local migration (if using alembic):

```powershell
cd backend
alembic upgrade head
```

---

If you'd like, I can add a one-shot script to reclassify existing unknown threats (example: mark empty -> `suspicious`) or add a debug route that shows raw grouped threat values.

License & credits
- MIT-style permissive license (add LICENSE file if desired).

---

Happy hacking — if something is unclear I can add exact `vite.config.js` proxy examples, a sample `.env` loader, or a small script to seed the DB with example URLs.
# Check current database version

alembic current
