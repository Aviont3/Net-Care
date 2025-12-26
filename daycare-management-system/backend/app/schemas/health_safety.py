# Health & Safety Schemas
# ============================================

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


# ============================================
# INCIDENT REPORT SCHEMAS
# ============================================

class IncidentReportBase(BaseModel):
    """Base incident report schema"""
    child_id: UUID
    incident_date: date
    incident_time: time
    incident_type: str  # injury, illness, behavioral, accident, other
    description: str
    circumstances: str
    injury_description: Optional[str] = None
    body_part_affected: Optional[str] = None
    action_taken: str
    witnesses: Optional[str] = None
    photo_url: Optional[str] = None
    parent_notified: bool = False
    parent_notified_at: Optional[datetime] = None
    parent_notification_method: Optional[str] = None  # phone, email, in-person, sms
    dcfs_notification_required: bool = False
    dcfs_notified_at: Optional[datetime] = None
    staff_signature_url: Optional[str] = None
    staff_signed_at: Optional[datetime] = None


class IncidentReportCreate(IncidentReportBase):
    """Schema for creating an incident report"""
    pass


class IncidentReportUpdate(BaseModel):
    """Schema for updating an incident report"""
    incident_type: Optional[str] = None
    description: Optional[str] = None
    circumstances: Optional[str] = None
    injury_description: Optional[str] = None
    body_part_affected: Optional[str] = None
    action_taken: Optional[str] = None
    witnesses: Optional[str] = None
    photo_url: Optional[str] = None
    parent_notified: Optional[bool] = None
    parent_notified_at: Optional[datetime] = None
    parent_notification_method: Optional[str] = None
    dcfs_notification_required: Optional[bool] = None
    dcfs_notified_at: Optional[datetime] = None
    staff_signature_url: Optional[str] = None
    staff_signed_at: Optional[datetime] = None


class IncidentReportResponse(IncidentReportBase):
    """Schema for incident report response"""
    id: UUID
    reported_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# MEDICATION AUTHORIZATION SCHEMAS
# ============================================

class MedicationAuthorizationBase(BaseModel):
    """Base medication authorization schema"""
    child_id: UUID
    medication_name: str
    dosage: str
    frequency: str  # once daily, twice daily, as needed, etc
    administration_instructions: str
    start_date: date
    end_date: Optional[date] = None
    prescribing_doctor: Optional[str] = None
    parent_signature_url: Optional[str] = None
    parent_signed_at: Optional[datetime] = None
    is_active: bool = True


class MedicationAuthorizationCreate(MedicationAuthorizationBase):
    """Schema for creating a medication authorization"""
    pass


class MedicationAuthorizationUpdate(BaseModel):
    """Schema for updating a medication authorization"""
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    administration_instructions: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    prescribing_doctor: Optional[str] = None
    parent_signature_url: Optional[str] = None
    parent_signed_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class MedicationAuthorizationResponse(MedicationAuthorizationBase):
    """Schema for medication authorization response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# MEDICATION LOG SCHEMAS
# ============================================

class MedicationLogBase(BaseModel):
    """Base medication log schema"""
    child_id: UUID
    authorization_id: UUID
    administration_date: date
    administration_time: time
    dosage_given: str
    staff_signature_url: Optional[str] = None
    notes: Optional[str] = None
    parent_notified: bool = False


class MedicationLogCreate(MedicationLogBase):
    """Schema for creating a medication log"""
    pass


class MedicationLogUpdate(BaseModel):
    """Schema for updating a medication log"""
    dosage_given: Optional[str] = None
    staff_signature_url: Optional[str] = None
    notes: Optional[str] = None
    parent_notified: Optional[bool] = None


class MedicationLogResponse(MedicationLogBase):
    """Schema for medication log response"""
    id: UUID
    administered_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
