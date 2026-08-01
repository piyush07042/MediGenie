"""
HTTP security headers middleware.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next,
    ):

        response = await call_next(request)

        response.headers["X-Content-Type-Options"] = "nosniff"

        response.headers["X-Frame-Options"] = "DENY"

        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["X-XSS-Protection"] = "1; mode=block"

        response.headers["Permissions-Policy"] = (
            "camera=(), microphone=(), geolocation=()"
        )

        return response


def configure_security_headers(
    app: FastAPI,
) -> None:

    app.add_middleware(
        SecurityHeadersMiddleware
    )