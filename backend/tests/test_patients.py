"""
Patient API tests.
"""

from __future__ import annotations

from fastapi import status


def get_access_token(client):

    register_payload = {
        "email": "doctor@test.com",
        "password": "Doctor123",
        "full_name": "Doctor",
        "role": "doctor",
    }

    client.post(
        "/api/v1/auth/register",
        json=register_payload,
    )

    login = client.post(
        "/api/v1/auth/login",
        data={
            "username": register_payload["email"],
            "password": register_payload["password"],
        },
    )

    return login.json()["data"]["access_token"]


def test_create_patient(client):

    token = get_access_token(client)

    payload = {
        "first_name": "John",
        "last_name": "Doe",
        "age": 42,
        "gender": "Male",
    }

    response = client.post(
        "/api/v1/patients/",
        json=payload,
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code in (
        status.HTTP_200_OK,
        status.HTTP_201_CREATED,
    )

    body = response.json()

    assert body["success"] is True


def test_list_patients(client):

    token = get_access_token(client)

    response = client.get(
        "/api/v1/patients/",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == status.HTTP_200_OK

    body = response.json()

    assert body["success"] is True

    assert isinstance(body["data"], list)