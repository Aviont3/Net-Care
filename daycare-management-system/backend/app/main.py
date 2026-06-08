
# FILE: backend/app/main.py
# FastAPI Application Entry Point


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, CSRFMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Daycare Management System for Netta's Bounce Around Daycare LLC - Chicago, IL",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# CORS Configuration - Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Middleware — rate limiting and security headers
# Order matters: SecurityHeaders wraps the response, RateLimit checks before processing
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    login_requests_per_minute=5,
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Netta's Bounce Around Daycare Management System API",
        "status": "online",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }

@app.get("/health")
async def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}
