"""
Health endpoint tests.
"""

from fastapi import status


def test_health(client):

    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["success"] is True

    assert "message" in body

    assert "data" in body