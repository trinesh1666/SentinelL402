from app.main import app


def test_root(client):
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["project"] == "SentinelL402"
    assert data["status"] == "running"
    assert data["version"] == "0.2.0"


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"