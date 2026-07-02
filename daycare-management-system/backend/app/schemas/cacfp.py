# CACFP (Child and Adult Care Food Program) Schemas
# ============================================

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
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


# ============================================
# MONTHLY CLAIM SCHEMAS
# ============================================

class MealBreakdownItem(BaseModel):
    """Per-meal-type reimbursement breakdown (preview only, not persisted)."""
    meal_type: str
    total_served: int
    free_meals: int
    reduced_meals: int
    paid_meals: int
    meal_amount: float
    ciu_amount: float
    subtotal: float


class CACFPClaimCalculation(BaseModel):
    """
    Response schema for the claim preview endpoint.
    Contains everything in a saved claim plus a per-meal breakdown.
    """
    claim_month: int
    claim_year: int
    operating_days: int
    total_attendance: int
    breakfast_count: int
    lunch_count: int
    supper_count: int
    snack_count: int
    free_enrolled: int
    reduced_enrolled: int
    paid_enrolled: int
    total_reimbursement: float
    breakdown: List[MealBreakdownItem] = []


class CACFPClaimCreate(BaseModel):
    """Schema for saving a calculated claim as a draft."""
    claim_month: int
    claim_year: int
    operating_days: int
    total_attendance: int
    breakfast_count: int
    lunch_count: int
    supper_count: int
    snack_count: int
    free_enrolled: int
    reduced_enrolled: int
    paid_enrolled: int
    total_reimbursement: float
    notes: Optional[str] = None


class CACFPClaimResponse(BaseModel):
    """Schema for a saved monthly claim."""
    id: UUID
    claim_month: int
    claim_year: int
    operating_days: int
    total_attendance: int
    breakfast_count: int
    lunch_count: int
    supper_count: int
    snack_count: int
    free_enrolled: int
    reduced_enrolled: int
    paid_enrolled: int
    total_reimbursement: Optional[Decimal] = None
    status: str
    submitted_at: Optional[datetime] = None
    submitted_by: Optional[UUID] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# AUDIT LOG SCHEMAS
# ============================================

class CACFPAuditLogResponse(BaseModel):
    """Schema for a single audit log entry."""
    id: UUID
    action: str
    entity_type: str
    entity_id: UUID
    field_changed: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None
    performed_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# ACTIVITY CORRECTION SCHEMA
# ============================================

class ActivityCorrectionRequest(BaseModel):
    """
    Schema for the POST /activities/{id}/correct endpoint.
    All corrections to CACFP meal records are logged immutably.
    """
    field: str           # name of the field being corrected
    new_value: str       # new value serialized to string
    reason: str          # required — auditor-visible explanation


# ============================================
# RECONCILIATION SCHEMA
# ============================================

class ReconciliationDayResult(BaseModel):
    date: str
    meal_count: int
    attendance_count: int
    valid: bool


class ReconciliationCheckResponse(BaseModel):
    days_checked: int
    all_valid: bool
    results: List[ReconciliationDayResult]
