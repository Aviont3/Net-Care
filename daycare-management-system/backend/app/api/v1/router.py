# Main API Router
# ============================================

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    children,
    parents,
    attendance,
    activities,
    emergency_contacts,
    authorized_pickup,
    compliance,
    incidents,
    medications
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(children.router, prefix="/children", tags=["Children"])
api_router.include_router(parents.router, prefix="/parents", tags=["Parents"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
api_router.include_router(emergency_contacts.router, prefix="/emergency-contacts", tags=["Emergency Contacts"])
api_router.include_router(authorized_pickup.router, prefix="/authorized-pickup", tags=["Authorized Pickup"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["DCFS Compliance"])
api_router.include_router(incidents.router, prefix="/incidents", tags=["Incident Reports"])
api_router.include_router(medications.router, prefix="/medications", tags=["Medications"])