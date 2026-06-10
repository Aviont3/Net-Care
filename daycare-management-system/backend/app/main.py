
# FILE: backend/app/main.py
# FastAPI Application Entry Point


import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.middleware.security import RateLimitMiddleware, SecurityHeadersMiddleware, CSRFMiddleware
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Daycare Management System for Netta's Bounce Around Daycare LLC - Chicago, IL",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Middleware stack — order matters!
# In Starlette, middleware added LAST wraps outermost (processes request first).
# CORSMiddleware MUST be outermost to handle OPTIONS preflight before other
# middleware can interfere. So we add it LAST.

# 1. Inner middleware: Security headers (wraps response)
app.add_middleware(SecurityHeadersMiddleware)
# 2. CSRF protection (validates origin on state-changing requests)
app.add_middleware(CSRFMiddleware)
# 3. Rate limiting
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    login_requests_per_minute=30,
)
# 4. CORS — outermost (added last). Handles OPTIONS preflight before
#    any other middleware processes the request.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

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
