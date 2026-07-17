from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_register_requires_valid_data():
    response = client.post(
        "/auth/register",
        json={},
    )

    assert response.status_code == 422

def test_get_me_requires_authentication():
    response = client.get("/auth/me")

    assert response.status_code == 401