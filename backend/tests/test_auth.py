"""
Authentication API tests.
"""

from fastapi import status


def test_register_user(client):

    payload = {
        "email": "doctor@test.com",
        "password": "Doctor123",
        "full_name": "Test Doctor",
        "role": "doctor",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
    )

    body = response.json()

    assert body["success"] is True


def test_duplicate_registration(client):

    payload = {
        "email": "doctor@test.com",
        "password": "Doctor123",
        "full_name": "Duplicate",
        "role": "doctor",
    }

    response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_invalid_login(client):

    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "doctor@test.com",
            "password": "WrongPassword",
        },
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED