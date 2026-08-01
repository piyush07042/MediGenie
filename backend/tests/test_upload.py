"""
Upload API tests.
"""

from __future__ import annotations

import io

from fastapi import status


def test_invalid_extension(client):

    response = client.post(
        "/api/v1/upload/report",
        files={
            "file": (
                "malware.exe",
                io.BytesIO(b"fake"),
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_empty_pdf(client):

    response = client.post(
        "/api/v1/upload/report",
        files={
            "file": (
                "report.pdf",
                io.BytesIO(b""),
                "application/pdf",
            )
        },
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST