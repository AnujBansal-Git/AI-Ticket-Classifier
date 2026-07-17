from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_bulk_job_requires_authentication():
    response = client.post(
        "/bulk-jobs",
        files={
            "file": (
                "tickets.csv",
                "ticket\nMy laptop is broken",
                "text/csv",
            )
        },
    )

    assert response.status_code == 401