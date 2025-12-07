K6 Load Test
===============

This folder contains a k6 script to run a simple load test against the backend.

Prerequisites
- Install `k6` (https://k6.io/docs/getting-started/installation)

Two simple modes are supported:
- `health` (no auth) — hits `GET /urls/health` repeatedly
- `search` (authenticated) — logs in once using `AUTH_USER`/`AUTH_PASS` and hits `GET /urls` with a query

Run examples (PowerShell)

1) Run a health check test (50 VUs, 30s) and export a summary JSON:

```powershell
cd tools/k6
# run 50 VUs for 30s and write summary to tools/k6/summary.json
k6 run --vus 50 --duration 30s --summary-export=summary.json load_test.js
```

2) Run an authenticated search test (login once then reuse token):

```powershell
cd tools/k6
$env:BASE_URL = "http://127.0.0.1:8000"
$env:VUS = "30"
$env:DURATION = "1m"
$env:TARGET = "search"
$env:AUTH_USER = "user"
$env:AUTH_PASS = "PA55_w0rd_user"
# Save summary JSON
k6 run --vus $env:VUS --duration $env:DURATION --summary-export=summary.json load_test.js
```

3) Save full metrics (raw output) as JSON as well:

```powershell
k6 run --vus 50 --duration 30s --out json=full_output.json --summary-export=summary.json load_test.js
```

Notes
- If your backend requires different host/port, set `BASE_URL` accordingly.
- The `search` mode will attempt to login once during the `setup()` phase; be careful not to hit the login endpoint with many VUs (the script avoids this by logging in only in setup).
- The produced `summary.json` contains k6's aggregated summary and can be inspected or archived.

Interpretation
- `summary.json` contains summary metrics (requests, checks, durations). Use it to compare runs.
