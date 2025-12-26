# DCFS Compliance Schemas
# ============================================

from datetime import date, datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


# ============================================
# ENROLLMENT FORM SCHEMAS
# ============================================

class EnrollmentFormBase(BaseModel):
    """Base enrollment form schema"""
    child_id: UUID
    enrollment_date: date
    parent_signature_url: Optional[str] = None
    parent_signed_at: Optional[datetime] = None
    staff_signature_url: Optional[str] = None
    staff_signed_at: Optional[datetime] = None
    form_data: Optional[Dict[str, Any]] = None
    is_complete: bool = False


class EnrollmentFormCreate(EnrollmentFormBase):
    """Schema for creating an enrollment form"""
    pass


class EnrollmentFormUpdate(BaseModel):
    """Schema for updating an enrollment form"""
    enrollment_date: Optional[date] = None
    parent_signature_url: Optional[str] = None
    parent_signed_at: Optional[datetime] = None
    staff_signature_url: Optional[str] = None
    staff_signed_at: Optional[datetime] = None
    form_data: Optional[Dict[str, Any]] = None
    is_complete: Optional[bool] = None


class EnrollmentFormResponse(EnrollmentFormBase):
    """Schema for enrollment form response"""
    id: UUID
    completed_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# IMMUNIZATION RECORD SCHEMAS
# ============================================

class ImmunizationRecordBase(BaseModel):
    """Base immunization record schema"""
    child_id: UUID
    vaccine_name: str
    administration_date: date
    expiration_date: Optional[date] = None
    document_url: Optional[str] = None
    provider_name: Optional[str] = None
    notes: Optional[str] = None
    is_verified: bool = False


class ImmunizationRecordCreate(ImmunizationRecordBase):
    """Schema for creating an immunization record"""
    pass


class ImmunizationRecordUpdate(BaseModel):
    """Schema for updating an immunization record"""
    vaccine_name: Optional[str] = None
    administration_date: Optional[date] = None
    expiration_date: Optional[date] = None
    document_url: Optional[str] = None
    provider_name: Optional[str] = None
    notes: Optional[str] = None
    is_verified: Optional[bool] = None


class ImmunizationRecordResponse(ImmunizationRecordBase):
    """Schema for immunization record response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# STAFF CREDENTIAL SCHEMAS
# ============================================

class StaffCredentialBase(BaseModel):
    """Base staff credential schema"""
    user_id: UUID
    credential_type: str  # CPR, First Aid, Background Check, TB Test, DCFS Training
    credential_number: Optional[str] = None
    issue_date: date
    expiration_date: Optional[date] = None
    document_url: Optional[str] = None
    is_verified: bool = False
    is_expired: bool = False


class StaffCredentialCreate(StaffCredentialBase):
    """Schema for creating a staff credential"""
    pass


class StaffCredentialUpdate(BaseModel):
    """Schema for updating a staff credential"""
    credential_type: Optional[str] = None
    credential_number: Optional[str] = None
    issue_date: Optional[date] = None
    expiration_date: Optional[date] = None
    document_url: Optional[str] = None
    is_verified: Optional[bool] = None
    is_expired: Optional[bool] = None


class StaffCredentialResponse(StaffCredentialBase):
    """Schema for staff credential response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
