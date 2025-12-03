import os

# Ensure test environment variables are set before importing the app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SINGLE_ADMIN_USERNAME", "admin")
os.environ.setdefault("SINGLE_ADMIN_PASSWORD", "changeme")
os.environ.setdefault("SECRET_KEY", "test-secret-123")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_get_health():
    r = client.get("/urls/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_auth_token_and_protected_delete():
    # Unauthenticated delete should be rejected
    r = client.delete("/urls/")
    assert r.status_code in (401, 403)

    # Obtain token using seeded admin
    r = client.post("/auth/token", data={"username": "admin", "password": "changeme"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "access_token" in body
    token = body["access_token"]

    # Use token to call protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    r = client.delete("/urls/", headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert "deleted" in j


def test_create_and_list_url():
    payload = {"url": "http://example.com", "domain": "example.com"}
    r = client.post("/urls/", json=payload)
    assert r.status_code == 200, r.text
    created = r.json()
    assert created.get("url") == "http://example.com"

    r = client.get("/urls/")
    assert r.status_code == 200
    urls = r.json()
    assert any(u.get("url") == "http://example.com" for u in urls)
