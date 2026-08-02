"""Compatibility PDF report generator for the reporting API."""

from __future__ import annotations

from typing import Any


def generate_clinical_pdf_report(report: dict[str, Any]) -> bytes:
    """Return a minimal placeholder PDF byte payload."""

    content = (
        "MediGenie Clinical Report\n"
        f"Patient: {report.get('patient').id if report.get('patient') else 'unknown'}\n"
        f"Summary: {report.get('summary').summary if report.get('summary') else 'No summary available'}\n"
    )

    return content.encode("utf-8")
