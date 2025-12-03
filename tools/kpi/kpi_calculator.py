#!/usr/bin/env python3
"""KPI calculator for performance tests.

Usage:
  python tools/kpi/kpi_calculator.py --k6-summary tools/k6/summary.json \
      [--import-results tools/k6/import_results.json]

This script parses a k6 summary JSON (use `k6 run --summary-export=summary.json`) and
optional import result JSON (list of objects with `inserted` and `duration_seconds`) to
compute:
 - request throughput (requests/sec)
 - latency percentiles (p50, p95, p99) in ms
 - error rate (failed requests / total)
 - rows/sec for import operations (if import results provided)

It prints a concise summary suitable for copy/paste into the performance section of the report.
"""
import json
import argparse
from pathlib import Path
from typing import Optional


def read_json(path: Path):
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def parse_k6_summary(summary: dict):
    # k6 summary JSON contains a `metrics` dict. We'll extract common fields.
    metrics = summary.get('metrics', {})
    out = {}

    # Requests per second (http_reqs)
    http_reqs = metrics.get('http_reqs')
    if http_reqs:
        out['requests_total'] = http_reqs.get('values', {}).get('count')
        out['rps'] = http_reqs.get('values', {}).get('rate') or http_reqs.get('values', {}).get('mean')

    # Status codes / checks
    checks = metrics.get('checks')
    if checks:
        out['checks_passed'] = checks.get('values', {}).get('passes')
        out['checks_failed'] = checks.get('values', {}).get('fails')
        total_checks = (out['checks_passed'] or 0) + (out['checks_failed'] or 0)
        out['error_rate'] = (out['checks_failed'] or 0) / total_checks if total_checks else None

    # Latency metrics (http_req_duration)
    dur = metrics.get('http_req_duration') or metrics.get('http_req_duration')
    if dur:
        vals = dur.get('values', {})
        out['avg_ms'] = vals.get('avg')
        out['min_ms'] = vals.get('min')
        out['max_ms'] = vals.get('max')
        # k6 uses percentiles in the summary under 'p(95)' etc sometimes in 'values'
        out['p50_ms'] = vals.get('p(50)') or vals.get('p50')
        out['p95_ms'] = vals.get('p(95)') or vals.get('p95')
        out['p99_ms'] = vals.get('p(99)') or vals.get('p99')

    # Iterations and vus
    iters = metrics.get('iterations')
    if iters:
        out['iterations'] = iters.get('values', {}).get('count')

    # duration (if provided in root)
    if 'root_summary' in summary and isinstance(summary['root_summary'], dict):
        out['duration_seconds'] = summary['root_summary'].get('duration')

    # Fallback: read `options` or top-level `duration` if present
    return out


def parse_import_results(path: Path):
    # Expect a JSON array of objects: {"inserted": int, "skipped": int, "duration_seconds": float}
    data = read_json(path)
    if not isinstance(data, list):
        data = [data]
    total_inserted = 0
    total_skipped = 0
    total_duration = 0.0
    for rec in data:
        total_inserted += int(rec.get('inserted', 0))
        total_skipped += int(rec.get('skipped', 0))
        total_duration += float(rec.get('duration_seconds', 0.0))
    rows_per_sec = (total_inserted / total_duration) if total_duration > 0 else None
    return {
        'total_inserted': total_inserted,
        'total_skipped': total_skipped,
        'total_duration_seconds': total_duration,
        'rows_per_sec': rows_per_sec,
    }


def print_report(k6_out: dict, import_out: Optional[dict]):
    print('\n=== Performance KPI Report ===')
    if k6_out:
        print('\n-- HTTP Test Summary (k6) --')
        if k6_out.get('requests_total') is not None:
            print(f"Total requests: {k6_out.get('requests_total')}")
        if k6_out.get('rps') is not None:
            print(f"Requests/sec (approx): {k6_out.get('rps'):.2f}")
        if k6_out.get('avg_ms') is not None:
            print(f"Avg latency: {k6_out.get('avg_ms'):.2f} ms")
        if k6_out.get('p50_ms') is not None:
            print(f"p50: {k6_out.get('p50_ms'):.2f} ms")
        if k6_out.get('p95_ms') is not None:
            print(f"p95: {k6_out.get('p95_ms'):.2f} ms")
        if k6_out.get('p99_ms') is not None:
            print(f"p99: {k6_out.get('p99_ms'):.2f} ms")
        if k6_out.get('error_rate') is not None:
            print(f"Error rate: {k6_out.get('error_rate')*100:.2f}%")

    if import_out:
        print('\n-- Import Results --')
        print(f"Inserted rows: {import_out['total_inserted']}")
        print(f"Skipped rows: {import_out['total_skipped']}")
        print(f"Total import duration: {import_out['total_duration_seconds']:.2f} s")
        if import_out['rows_per_sec'] is not None:
            print(f"Rows/sec: {import_out['rows_per_sec']:.2f} rows/s")

    print('\nTips: include CPU/memory samples (docker stats) and DB EXPLAIN ANALYZE output in the report.')


def main():
    parser = argparse.ArgumentParser(description='KPI calculator for k6 and import tests')
    parser.add_argument('--k6-summary', type=Path, help='Path to k6 summary JSON (use --summary-export)')
    parser.add_argument('--import-results', type=Path, help='Path to JSON file with import results (inserted/skipped/duration_seconds)')
    args = parser.parse_args()

    k6_out = None
    import_out = None
    if args.k6_summary:
        summary = read_json(args.k6_summary)
        # k6 stores the metrics at the top-level 'metrics' key
        k6_out = parse_k6_summary(summary)
    if args.import_results:
        import_out = parse_import_results(args.import_results)

    print_report(k6_out or {}, import_out)


if __name__ == '__main__':
    main()
