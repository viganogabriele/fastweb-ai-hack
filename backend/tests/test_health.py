from fastapi.testclient import TestClient

from tessera.api.main import app


def test_health() -> None:
    r = TestClient(app).get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
