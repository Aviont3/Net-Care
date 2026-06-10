"""Security middleware for Net-Care API.
Implements: rate limiting (#7), CSRF protection (#8), security headers (#6, #11).
"""
import time
from collections import defaultdict
from urllib.parse import urlparse

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings


# ============================================
# RATE LIMITING (Issue #7)
# ============================================
class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiter.
    - 100 requests/min for general endpoints
    - 5 requests/min for login (brute-force protection)

    Note: For multi-process production, replace with Redis-backed limiter.
    """

    def __init__(self, app, requests_per_minute: int = 100, login_requests_per_minute: int = 5):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.login_requests_per_minute = login_requests_per_minute
        self.requests: dict = defaultdict(list)

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()

        # Clean entries older than 60 seconds
        self.requests[client_ip] = [t for t in self.requests[client_ip] if now - t < 60]

        # Stricter limit for login endpoint
        path = request.url.path
        limit = self.login_requests_per_minute if "/auth/login" in path else self.requests_per_minute

        if len(self.requests[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."},
                headers={"Retry-After": "60"},
            )

        self.requests[client_ip].append(now)
        response = await call_next(request)
        return response


# ============================================
# CSRF PROTECTION (Issue #8)
# ============================================
class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection via Origin/Referer validation.

    For JWT Bearer-token APIs, CSRF is less of a concern since tokens
    aren't auto-sent by browsers. However, this adds defense-in-depth
    by validating the Origin header on state-changing requests (POST, PUT,
    PATCH, DELETE) to ensure they come from trusted origins.
    """

    UNSAFE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

    async def dispatch(self, request: Request, call_next):
        # Let CORS preflight through — OPTIONS must be handled by CORSMiddleware
        if request.method == "OPTIONS":
            return await call_next(request)

        if request.method in self.UNSAFE_METHODS:
            origin = request.headers.get("origin")
            referer = request.headers.get("referer")

            # Allow requests with no origin (e.g., server-to-server, mobile apps, curl)
            # Browsers always send Origin on cross-origin requests
            if origin:
                allowed_origins = settings.BACKEND_CORS_ORIGINS
                if isinstance(allowed_origins, str):
                    allowed_origins = [o.strip() for o in allowed_origins.split(",")]

                if origin not in allowed_origins:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF validation failed: origin not allowed"},
                    )
            elif referer:
                # Fallback: check referer if origin header not present
                parsed = urlparse(referer)
                referer_origin = f"{parsed.scheme}://{parsed.netloc}"
                allowed_origins = settings.BACKEND_CORS_ORIGINS
                if isinstance(allowed_origins, str):
                    allowed_origins = [o.strip() for o in allowed_origins.split(",")]

                if referer_origin not in allowed_origins:
                    return JSONResponse(
                        status_code=403,
                        content={"detail": "CSRF validation failed: referer not allowed"},
                    )

        response = await call_next(request)
        return response


# ============================================
# SECURITY HEADERS (Issues #6, #11)
# ============================================
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses:
    - Strict-Transport-Security (HSTS) — enforce HTTPS
    - X-Frame-Options — prevent clickjacking
    - X-Content-Type-Options — prevent MIME sniffing
    - X-XSS-Protection — legacy XSS filter
    - Referrer-Policy — limit referrer info leakage
    - Permissions-Policy — restrict browser features
    - Content-Security-Policy — restrict resource loading
    """

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # HSTS — enforce HTTPS (Issue #6)
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # XSS protection (legacy browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy (restrict browser APIs)
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self' https://api.openai.com"
        )

        return response
