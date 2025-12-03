"""Simple auth sanity-check script.

Runs without starting the HTTP server. Verifies:
- `get_password_hash` and `verify_password`
- `create_access_token` produces a decodable JWT

Usage: (from repo root)
    $env:PYTHONPATH='backend'; python backend/tools/test_auth.py
"""
from app.utils import security
import os


def main():
    pw = os.getenv("TEST_PASSWORD", "testpass")
    username = os.getenv("TEST_USERNAME", "tester")

    hashed = security.get_password_hash(pw)
    verified = security.verify_password(pw, hashed)
    token = security.create_access_token({"sub": username})

    print("password:", pw)
    print("hashed:", hashed)
    print("verified:", verified)
    print("token:", token)

    # try decoding JWT to confirm signature using project's helper
    try:
        payload = security.decode_access_token(token)
        print("token_payload:", payload)
    except Exception as e:
        print("failed to decode token:", e)


if __name__ == "__main__":
    main()
