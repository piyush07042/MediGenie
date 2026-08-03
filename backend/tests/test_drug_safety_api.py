"""Drug Safety API tests."""

from __future__ import annotations

from fastapi import status


def test_drug_safety_analyze_store_and_get_patient(client):
    response = client.post(
        "/api/v1/drug-safety/analyze",
        json={
            "medications": ["aspirin", "warfarin"],
            "allergies": ["penicillin"],
        },
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["success"] is True
    assert body["data"]["drug_safety_assessment"]["status"] in {"PASS", "FLAGGED"}

    store_response = client.post(
        "/api/v1/drug-safety/store",
        json={
            "patient_id": None,
            "medications": ["aspirin", "warfarin"],
            "allergies": ["penicillin"],
        },
    )

    assert store_response.status_code == status.HTTP_200_OK
    store_body = store_response.json()
    assert store_body["success"] is True
    assert "id" in store_body["data"]

    assessment_id = store_body["data"]["id"]
    get_response = client.get(f"/api/v1/drug-safety/assessment/{assessment_id}")

    assert get_response.status_code == status.HTTP_200_OK
    get_body = get_response.json()
    assert get_body["success"] is True
    assert get_body["data"]["id"] == assessment_id
    assert get_body["data"]["assessment"]["drug_safety_assessment"]["status"] in {"PASS", "FLAGGED"}
