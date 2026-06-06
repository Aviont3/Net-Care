# Net-Care Changelog

All notable changes to this project will be documented in this file.
Format follows [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased] — feature/security-hardening-week1

### 2026-06-06 — Security Hardening Sprint Started

#### ✅ Completed

**Commit: "security: remove debug prints leaking PII, add structured logging"**
- Removed 11 `print()` statements from `backend/app/core/security.py` that were leaking JWT tokens, decoded payloads, user emails, and DB session objects on every authenticated request
- Added `import logging` / `logger = logging.getLogger(__name__)` with safe log statements (`logger.debug` for normal flow, `logger.warning` for auth failures)
- Removed 6 `console.log` lines from `frontend/src/services/api.ts` that leaked partial token values in the Axios request interceptor
- Kept legitimate `console.error` calls in the response error handler

**Commit: "security: lock registration to admin-only, add .env.example, reduce token expiry to 15min"**
- Locked `POST /api/v1/auth/register` endpoint — now requires `get_current_admin_user` dependency (unauthenticated or non-admin requests rejected)
- Fixed duplicate `get_current_user` import in `auth.py` (was imported from both `app.core.security` and `app.dependencies`)
- Created `.env.example` with all required environment variables documented (no secrets)
- Reduced `ACCESS_TOKEN_EXPIRE_MINUTES` default from 30 → 15

---

#### 🎫 GitHub Issues Created (Scrumboard)

**Done (completed):**
- #3: Remove debug print statements & add structured logging
- #4: Replace hardcoded secrets with environment variables
- #5: Add input validation & sanitization

**Todo (security hardening):**
- #6: Implement HTTPS-only with HSTS headers
- #7: Set up rate limiting on login & API endpoints
- #8: Add CSRF protection to all forms
- #9: Implement session timeout & token rotation
- #10: Configure CORS policy (allow only trusted origins)
- #11: Add security response headers (CSP, X-Frame-Options, etc.)
- #12: Write security audit tests (OWASP Top 10 coverage)

**Todo (feature sprint — with full developer descriptions):**
- #13: Wire AdminDashboard to real API data (P0, Week 1)
- #14: Build Activities page (P1, Week 2)
- #15: Implement AI Daily Reports — template MVP (P1, Week 2)
- #16: Build Incidents page — DCFS format (P1, Week 3)
- #17: Build Medications page (P1, Week 3)
- #19: Parent Portal MVP (P2, Week 3)
- #20: Deploy to production — Railway/Render (P2, Week 4)
- #21: Testing infrastructure (P2, Week 4)

---

## Notes

- **Branch**: `feature/security-hardening-week1`
- **Board**: https://github.com/users/Aviont3/projects/1
- **Repo**: https://github.com/Aviont3/Net-Care
