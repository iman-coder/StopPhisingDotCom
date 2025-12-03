#!/usr/bin/env python3
"""Generate CSV files for performance tests.
Usage:
  python tools/generate_csv.py 10000 test_10k.csv
Generates a CSV with header URL,Domain,Threat and N rows.
"""
import csv
import sys

def generate(n, out_path):
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["URL", "Domain", "Threat"])
        for i in range(int(n)):
            url = f"https://example{i}.com/path?id={i}"
            domain = f"example{i}.com"
            threat = "benign"
            w.writerow([url, domain, threat])

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python tools/generate_csv.py <rows> <output.csv>")
        sys.exit(1)
    rows = int(sys.argv[1])
    out = sys.argv[2]
    print(f"Generating {rows} rows to {out}...")
    generate(rows, out)
    print("Done")
