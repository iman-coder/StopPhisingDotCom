#!/usr/bin/env python3
"""Post a CSV to the backend import endpoint and record the result.

Saves a JSON file (array) with objects: {inserted, skipped, duration_seconds} so
`kpi_calculator.py` can compute rows/sec.

Usage:
  python tools/kpi/post_import_and_record.py --file tools/k6/test.csv \
      --out tools/k6/import_results.json --url http://localhost:8000/urls/import

Requires: `requests` (pip install requests)
"""
import argparse
import time
import json
from pathlib import Path

try:
    import requests  # type: ignore
except Exception:
    requests = None


def _encode_multipart(filename: str, file_bytes: bytes, boundary: str):
    # Build a simple multipart/form-data body for a single file field named 'file'
    import mimetypes

    ct, _ = mimetypes.guess_type(filename)
    if not ct:
        ct = 'application/octet-stream'
    lines = []
    lines.append(f'--{boundary}')
    lines.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
    lines.append(f'Content-Type: {ct}')
    lines.append('')
    body = '\r\n'.join(lines).encode('utf-8') + b'\r\n' + file_bytes + b'\r\n'
    ending = (f'--{boundary}--\r\n').encode('utf-8')
    return body + ending


def post_file(file_path: Path, url: str, out_path: Path):
    """POST the file and record a result entry. Uses requests if available, else stdlib."""
    file_bytes = file_path.read_bytes()

    start = time.perf_counter()
    if requests is not None:
        resp = requests.post(url, files={'file': (file_path.name, file_bytes, 'text/csv')})
    else:
        # stdlib fallback
        import urllib.request

        boundary = '----WebKitFormBoundary' + str(int(time.time() * 1000))
        body = _encode_multipart(file_path.name, file_bytes, boundary)
        req = urllib.request.Request(url, data=body, method='POST')
        req.add_header('Content-Type', f'multipart/form-data; boundary={boundary}')
        try:
            with urllib.request.urlopen(req) as r:
                resp_body = r.read()
                status_code = r.getcode()
                resp_text = resp_body.decode('utf-8', errors='replace')
                class _R:
                    def __init__(self, code, text):
                        self.status_code = code
                        self._text = text

                    def json(self):
                        try:
                            return json.loads(self._text)
                        except Exception:
                            return {'text': self._text}

                    @property
                    def text(self):
                        return self._text

                resp = _R(status_code, resp_text)
        except Exception as e:
            duration = time.perf_counter() - start
            print('Request failed:', e)
            resp = type('R', (), {'status_code': 0, 'text': str(e), 'json': lambda self=None: {'text': str(e)}})()
    duration = time.perf_counter() - start

    try:
        body = resp.json()
    except Exception:
        body = {'status_code': getattr(resp, 'status_code', None), 'text': getattr(resp, 'text', '')}

    # Expected body contains inserted/skipped counts. Normalize
    inserted = body.get('inserted') if isinstance(body, dict) else None
    skipped = body.get('skipped') if isinstance(body, dict) else None

    rec = {
        'inserted': int(inserted) if inserted is not None else 0,
        'skipped': int(skipped) if skipped is not None else 0,
        'duration_seconds': duration,
        'status_code': getattr(resp, 'status_code', 0),
    }

    # Append to out_path (create array if not exists)
    data = []
    if out_path.exists():
        try:
            data = json.loads(out_path.read_text(encoding='utf-8'))
            if not isinstance(data, list):
                data = [data]
        except Exception:
            data = []

    data.append(rec)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    print('Wrote result to', out_path)
    print(json.dumps(rec, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, type=Path, help='CSV file to upload')
    parser.add_argument('--url', default='http://localhost:8000/urls/import', help='Import endpoint URL')
    parser.add_argument('--out', default=Path('tools/k6/import_results.json'), type=Path, help='Output JSON file')
    args = parser.parse_args()

    if not args.file.exists():
        raise SystemExit(f'CSV file not found: {args.file}')

    post_file(args.file, args.url, args.out)


if __name__ == '__main__':
    main()
