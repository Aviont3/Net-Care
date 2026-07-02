# CACFP (Child and Adult Care Food Program) Schemas
# ============================================

from datetime import date, datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class CACFPEligibilityCreate(BaseModel):
    """Schema for creating a CACFP eligibility record."""
    child_id: UUID
    eligibility_tier: str  # free, reduced, paid
    determination_date: date
    expiration_date: date
    determination_method: str  # e.g. household_application, categorical, provider_household
    notes: Optional[str] = None


class CACFPEligibilityUpdate(BaseModel):
    """Schema for updating a CACFP eligibility record. All fields optional."""
    eligibility_tier: Optional[str] = None
    expiration_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class CACFPEligibilityResponse(BaseModel):
    """Schema for CACFP eligibility response."""
    id: UUID
    child_id: UUID
    eligibility_tier: str
    determination_date: date
    expiration_date: date
    determination_method: str
    is_active: bool
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
