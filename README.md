# URL Management & Dashboard Project

This project is a web application for monitoring and managing URLs. It consists of a Vue 3 frontend and a Python backend (FastAPI). The frontend displays dashboards and allows URL CRUD operations, while the backend exposes APIs to provide data and handle requests.

---

## 1️⃣ Project Summary

### Frontend
- Built with **Vue 3** using Composition API.
- Provides:
  - Dashboard with metrics, charts, and search.
  - URL management (Add, Edit, Delete, Import/Export CSV).
  - Reusable components for charts and forms.

### Backend
- Built with **Python FastAPI**.
- Provides REST APIs for:
  - Dashboard metrics.
  - URL CRUD operations.
  - CSV import/export.
- Logs URL actions for tracking changes.

---

## 2️⃣ API Endpoints

### Dashboard Services (11 endpoints)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /dashboard/globalMetrics | GET | Get total URLs, safe, suspicious, malicious counts |
| /dashboard/riskDistribution | GET | Get risk distribution (pie chart) |
| /dashboard/statusDistribution | GET | Get status distribution (pie chart) |
| /dashboard/domainCounts | GET | Count of URLs per domain |
| /dashboard/topRiskyDomains | GET | Top domains with most risky URLs |
| /dashboard/monthlyActivity | GET | Number of scanned URLs per month (line chart) |
| /dashboard/dailyActivity | GET | Number of scanned URLs per day (line chart) |
| /dashboard/topRiskyUrls | GET | Top risky URLs list |
| /dashboard/mostRecentUrls | GET | Most recently added URLs |
| /dashboard/recentEvents | GET | Recent actions/events on URLs |
| /dashboard/search | GET (?q=...) | Search URLs/domains |

### URL CRUD Services (6 endpoints including CSV)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| /urls | GET | Get all URLs |
| /urls | POST | Add a new URL |
| /urls/:id | PUT | Update an existing URL |
| /urls/:id | DELETE | Delete a URL |
| /urls/import | POST | Upload CSV to add multiple URLs |
| /urls/export | GET | Download all URLs as CSV |

**Summary of APIs**

| Section | Number of APIs |
|---------|----------------|
| Dashboard | 11 |
| URL CRUD + CSV | 6 |
| **Total** | 17 |

---

## 3️⃣ File Structure

### Frontend (Vue 3)

```bash
frontend/
├─ public/
│ └─ index.html
├─ src/
│ ├─ assets/
│ ├─ components/
│ │ ├─ AddUrlForm.vue
│ │ ├─ UrlTable.vue
│ │ ├─ ImportCsv.vue
│ │ ├─ ExportCsv.vue
│ │ └─ charts/
│ │ ├─ PieChart.vue
│ │ └─ LineChart.vue
│ ├─ services/
│ │ ├─ dashboardService.js
│ │ └─ urlService.js
│ ├─ views/
│ │ ├─ Dashboard.vue
│ │ └─ URLs.vue
│ ├─ App.vue
│ └─ main.js
├─ package.json
└─ vite.config.js
```
### Backend (Python + FastAPI)

```bash
backend/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│
│   ├── routes/
│   │   ├── urls.py
│   │   └── dashboard.py
│
│   ├── services/
│   │   ├── csv_service.py
│   │   ├── url_service.py
│   │   └── dashboard_service.py
│
│   ├── utils/
│   │   ├── logger.py
│   │   └── database.py          
│   │   └── parser.py  (optional)
│
│   ├── migrations/
│
└── requirements.txt
```
---
### other files
```bash
flatten_JSON.py
merge.py
Prepare_data.py
README.md
remove_unwanted_data.py
urls_merged_crud1.csv #the final URL's collection
```
**Notes:**
- `frontend/src/services/` contains all API calls.
- `frontend/src/components/charts/` has reusable chart components.
- `backend/app/routes/` separates dashboard and URL management endpoints.
- `backend/app/utils/logger.py` is for logging URL actions.
- `venv/` should be added to `.gitignore`.
---
# set up commands
## Backend commands
### 1. Activate Python environment
```bash
# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
```
## Database migrations
```bash
# Generate a new migration after changing models
alembic revision --autogenerate -m "migration_name"

# Apply migrations to the database
alembic upgrade head

# Rollback to a previous migration
alembic downgrade -1

# Check current database version
alembic current
```

## run the backend server
```bash
uvicorn app.main:app --reload
```
### running the tests
```bash
pytest -q
```
### Test api endpoints
```bash
http GET http://localhost:8000/urls
http POST http://localhost:8000/urls url="http://example.com" domain="example.com"
```
## frontend commands
### install dependencies
```bash
npm install
```
### Run development server
```bash
npm run dev
```
### Build for production
```bash
npm run build
```
### Preview production build
```bash
npm run preview
```
---

## 4️⃣ Next Steps
- Implement backend database & services.
- Connect frontend to backend APIs.
- Optionally add authentication & user management in the future.

