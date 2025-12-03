Performance test tools

This file describes how to run basic performance tests against the running backend.

Prerequisites
- Backend running at http://localhost:8000 (when running k6 in host machine) or use host.docker.internal in Docker containers on Windows.
- Docker installed (optional) to run k6 Docker image.
- Python 3.8+ to run `tools/generate_csv.py`.

Generate a CSV for tests

```powershell
python tools\generate_csv.py 10000 tools\k6\test.csv
```

Run import load test with k6 (local k6 installed)

```powershell
# if you have k6 installed locally
k6 run tools\k6\import_test.js

# or using Docker (will mount current folder)
docker run --rm -v ${PWD}:/src -w /src loadimpact/k6 run /src/tools/k6/import_test.js
```

Run dashboard read test

```powershell
k6 run tools\k6\dashboard_test.js
# or via Docker
docker run --rm -v ${PWD}:/src -w /src loadimpact/k6 run /src/tools/k6/dashboard_test.js
```

Notes
- The import test expects the CSV to be at `tools/k6/test.csv` (k6 `open()` reads relative to script path when mounted). Use `tools/generate_csv.py` to produce it.
- The import script posts to `http://host.docker.internal:8000/urls/import` because k6 running in Docker needs that host alias on Windows. If you run k6 on host, change URL to `http://localhost:8000/urls/import`.
- Tune `vus` and `duration` in the k6 scripts to increase load.
- Collect `docker stats` and database `EXPLAIN ANALYZE` outputs while tests run.
