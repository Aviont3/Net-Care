"""
Security Audit Tests — OWASP Top 10 Coverage
=============================================
Issue #12: Write security audit tests covering OWASP Top 10 vulnerabilities.

Test categories:
  A01: Broken Access Control
  A02: Cryptographic Failures
  A03: Injection
  A04: Insecure Design
  A05: Security Misconfiguration
  A06: Vulnerable Components (manual check)
  A07: Authentication Failures
  A08: Data Integrity Failures
  A09: Logging & Monitoring
  A10: Server-Side Request Forgery (N/A for this app currently)
"""
import pytest
import time
from fastapi.testclient import TestClient
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from datetime import timedelta


# ============================================
# A01: BROKEN ACCESS CONTROL
# ============================================
class TestBrokenAccessControl:
    """Tests for authorization and access control."""

    def test_unauthenticated_access_denied(self, client: TestClient):
        """Protected endpoints reject requests without auth tokens."""
        protected_endpoints = [
            ("GET", f"{settings.API_V1_PREFIX}/children/"),
            ("GET", f"{settings.API_V1_PREFIX}/auth/me"),
            ("GET", f"{settings.API_V1_PREFIX}/dashboard/summary"),
        ]
        for method, url in protected_endpoints:
            response = client.request(method, url)
            assert response.status_code in (401, 403), (
                f"{method} {url} returned {response.status_code} without auth"
            )

    def test_invalid_token_rejected(self, client: TestClient):
        """Forged/invalid JWT tokens are rejected."""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get(f"{settings.API_V1_PREFIX}/auth/me", headers=headers)
        assert response.status_code == 401

    def test_expired_token_rejected(self, client: TestClient, test_user):
        """Expired tokens are rejected."""
        expired_token = create_access_token(
            data={"sub": test_user.email},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get(f"{settings.API_V1_PREFIX}/auth/me", headers=headers)
        assert response.status_code == 401

    def test_register_requires_admin(self, client: TestClient, auth_headers):
        """Non-admin users cannot register new users."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/register",
            json={
                "email": "hacker@evil.com",
                "password": "hackpass123",
                "first_name": "Hack",
                "last_name": "Er",
                "role": "admin"
            },
            headers=auth_headers  # staff user, not admin
        )
        assert response.status_code == 403

    def test_no_horizontal_privilege_escalation(self, client: TestClient, auth_headers):
        """Users cannot modify their own role via API manipulation."""
        # Attempt to access admin-only endpoints as staff
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/register",
            json={
                "email": "new@test.com",
                "password": "pass123",
                "first_name": "New",
                "last_name": "User",
                "role": "staff"
            },
            headers=auth_headers
        )
        assert response.status_code == 403


# ============================================
# A02: CRYPTOGRAPHIC FAILURES
# ============================================
class TestCryptographicFailures:
    """Tests for proper use of cryptography."""

    def test_passwords_not_in_response(self, client: TestClient, admin_headers, db):
        """Password hashes are never returned in API responses."""
        response = client.get(
            f"{settings.API_V1_PREFIX}/auth/me",
            headers=admin_headers
        )
        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data

    def test_token_is_signed_jwt(self, client: TestClient, test_user):
        """Login returns a properly signed JWT (3 segments)."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": test_user.email, "password": "testpass123"}
        )
        token = response.json()["access_token"]
        parts = token.split(".")
        assert len(parts) == 3, "JWT should have 3 dot-separated segments"

    def test_refresh_token_is_separate(self, client: TestClient, test_user):
        """Login returns a refresh token distinct from access token."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": test_user.email, "password": "testpass123"}
        )
        data = response.json()
        assert "refresh_token" in data
        assert data["refresh_token"] != data["access_token"]


# ============================================
# A03: INJECTION
# ============================================
class TestInjection:
    """Tests for SQL injection and command injection."""

    def test_sql_injection_login_email(self, client: TestClient):
        """SQL injection in login email field is rejected."""
        payloads = [
            "' OR '1'='1",
            "admin@test.com'; DROP TABLE users; --",
            "\" OR \"\"=\"",
            "1' UNION SELECT * FROM users --",
        ]
        for payload in payloads:
            response = client.post(
                f"{settings.API_V1_PREFIX}/auth/login",
                data={"username": payload, "password": "anything"}
            )
            # Should fail auth, not crash
            assert response.status_code in (401, 422), (
                f"SQL injection payload not properly handled: {payload}"
            )

    def test_sql_injection_search_params(self, client: TestClient, auth_headers):
        """SQL injection in query parameters is handled safely."""
        response = client.get(
            f"{settings.API_V1_PREFIX}/children/?search=' OR 1=1 --",
            headers=auth_headers
        )
        # Should not crash — 200 with empty results or 422 validation error
        assert response.status_code in (200, 404, 422)


# ============================================
# A05: SECURITY MISCONFIGURATION
# ============================================
class TestSecurityMisconfiguration:
    """Tests for security headers and configuration."""

    def test_security_headers_present(self, client: TestClient):
        """All security headers are set on responses."""
        response = client.get("/health")
        headers = response.headers

        assert "strict-transport-security" in headers
        assert "x-frame-options" in headers
        assert headers["x-frame-options"] == "DENY"
        assert "x-content-type-options" in headers
        assert headers["x-content-type-options"] == "nosniff"
        assert "x-xss-protection" in headers
        assert "referrer-policy" in headers
        assert "content-security-policy" in headers
        assert "permissions-policy" in headers

    def test_hsts_max_age_sufficient(self, client: TestClient):
        """HSTS max-age is at least 1 year (31536000 seconds)."""
        response = client.get("/health")
        hsts = response.headers.get("strict-transport-security", "")
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts

    def test_cors_not_wildcard(self, client: TestClient):
        """CORS does not allow wildcard origins."""
        # Make a request with a malicious origin
        response = client.options(
            f"{settings.API_V1_PREFIX}/auth/login",
            headers={
                "Origin": "https://evil.com",
                "Access-Control-Request-Method": "POST"
            }
        )
        # Should not return evil.com as allowed origin
        allowed_origin = response.headers.get("access-control-allow-origin", "")
        assert allowed_origin != "*"
        assert "evil.com" not in allowed_origin

    def test_no_server_version_leak(self, client: TestClient):
        """Server header does not leak version info."""
        response = client.get("/health")
        server = response.headers.get("server", "")
        # Should not contain specific version numbers
        assert "Python" not in server or "version" not in server.lower()


# ============================================
# A07: IDENTIFICATION & AUTHENTICATION FAILURES
# ============================================
class TestAuthenticationFailures:
    """Tests for authentication security."""

    def test_rate_limiting_on_login(self, client: TestClient, test_user):
        """Login endpoint is rate-limited to prevent brute force."""
        # Make 6 rapid login attempts (limit is 5/min)
        for i in range(6):
            response = client.post(
                f"{settings.API_V1_PREFIX}/auth/login",
                data={"username": "brute@force.com", "password": f"attempt{i}"}
            )
        # The 6th attempt should be rate-limited
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_generic_login_error_message(self, client: TestClient):
        """Login errors don't reveal whether email exists."""
        # Non-existent email
        r1 = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "nonexistent@test.com", "password": "wrong"}
        )
        # Existing email, wrong password
        r2 = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "test@example.com", "password": "wrongpass"}
        )
        # Both should return same generic error
        assert r1.status_code == r2.status_code == 401
        assert r1.json()["detail"] == r2.json()["detail"]

    def test_inactive_user_cannot_login(self, client: TestClient, db):
        """Inactive/disabled users cannot authenticate."""
        from app.core.security import get_password_hash
        from app.models.user import User

        inactive_user = User(
            email="inactive@test.com",
            password_hash=get_password_hash("password123"),
            first_name="Inactive",
            last_name="User",
            role="staff",
            is_active=False
        )
        db.add(inactive_user)
        db.commit()

        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "inactive@test.com", "password": "password123"}
        )
        assert response.status_code == 403

    def test_token_rotation_works(self, client: TestClient, test_user):
        """Refresh token endpoint issues new token pair."""
        # Login to get tokens
        login_response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": test_user.email, "password": "testpass123"}
        )
        refresh_token = login_response.json()["refresh_token"]

        # Use refresh token to get new pair
        refresh_response = client.post(
            f"{settings.API_V1_PREFIX}/auth/refresh",
            json={"refresh_token": refresh_token}
        )
        assert refresh_response.status_code == 200
        new_data = refresh_response.json()
        assert "access_token" in new_data
        assert "refresh_token" in new_data
        # New tokens should be different from original
        assert new_data["refresh_token"] != refresh_token

    def test_invalid_refresh_token_rejected(self, client: TestClient):
        """Invalid refresh tokens are rejected."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/refresh",
            json={"refresh_token": "invalid.token.here"}
        )
        assert response.status_code == 401

    def test_access_token_cannot_be_used_as_refresh(self, client: TestClient, test_user):
        """Access tokens cannot be used in place of refresh tokens."""
        login_response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": test_user.email, "password": "testpass123"}
        )
        access_token = login_response.json()["access_token"]

        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/refresh",
            json={"refresh_token": access_token}
        )
        assert response.status_code == 401


# ============================================
# A08: SOFTWARE & DATA INTEGRITY FAILURES
# ============================================
class TestDataIntegrityFailures:
    """Tests for CSRF and data integrity."""

    def test_csrf_blocks_cross_origin_post(self, client: TestClient):
        """POST from untrusted origin is blocked by CSRF middleware."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "test@example.com", "password": "test"},
            headers={"Origin": "https://evil-site.com"}
        )
        assert response.status_code == 403
        assert "CSRF" in response.json().get("detail", "")

    def test_csrf_allows_trusted_origin(self, client: TestClient, test_user):
        """POST from trusted origin is allowed."""
        trusted_origin = "http://localhost:5173"
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": test_user.email, "password": "testpass123"},
            headers={"Origin": trusted_origin}
        )
        # Should proceed normally (not blocked by CSRF)
        assert response.status_code in (200, 401)  # auth result, not 403

    def test_csrf_allows_no_origin(self, client: TestClient):
        """Requests without Origin header are allowed (API clients, curl)."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "test@example.com", "password": "test"}
            # No Origin header
        )
        # Should not be blocked by CSRF
        assert response.status_code != 403


# ============================================
# A09: SECURITY LOGGING & MONITORING
# ============================================
class TestSecurityLogging:
    """Tests for security logging coverage."""

    def test_failed_login_returns_401(self, client: TestClient):
        """Failed logins return 401 (logged for monitoring)."""
        response = client.post(
            f"{settings.API_V1_PREFIX}/auth/login",
            data={"username": "wrong@test.com", "password": "wrong"}
        )
        assert response.status_code == 401

    def test_health_check_available(self, client: TestClient):
        """Health check endpoint works (for monitoring tools)."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ============================================
# GENERAL SECURITY
# ============================================
class TestGeneralSecurity:
    """General security best practices."""

    def test_token_expiry_is_short(self):
        """Access token expiry is 15 minutes or less."""
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES <= 15

    def test_debug_mode_disabled_in_production(self):
        """DEBUG should be False in non-development environments."""
        if settings.ENVIRONMENT != "development":
            assert settings.DEBUG is False

    def test_no_default_secret_key(self):
        """SECRET_KEY is not a default/placeholder value."""
        dangerous_defaults = ["secret", "changeme", "your-secret-key", ""]
        assert settings.SECRET_KEY.lower() not in dangerous_defaults
