# Parent Communication Schemas
# ============================================

from datetime import date, datetime
from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel


# ============================================
# DAILY REPORT SCHEMAS
# ============================================

class DailyReportBase(BaseModel):
    """Base daily report schema"""
    child_id: UUID
    report_date: date
    ai_generated_summary: Optional[str] = None
    custom_notes: Optional[str] = None
    overall_mood: Optional[str] = None
    sent_to_parents: bool = False
    sent_at: Optional[datetime] = None
    activities_summary: Optional[Dict[str, Any]] = None


class DailyReportCreate(BaseModel):
    """Schema for creating a daily report"""
    child_id: UUID
    report_date: date
    custom_notes: Optional[str] = None
    overall_mood: Optional[str] = None


class DailyReportUpdate(BaseModel):
    """Schema for updating a daily report"""
    ai_generated_summary: Optional[str] = None
    custom_notes: Optional[str] = None
    overall_mood: Optional[str] = None
    sent_to_parents: Optional[bool] = None
    sent_at: Optional[datetime] = None
    activities_summary: Optional[Dict[str, Any]] = None


class DailyReportResponse(DailyReportBase):
    """Schema for daily report response"""
    id: UUID
    generated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DailyReportGenerate(BaseModel):
    """Schema for triggering AI generation of daily report"""
    child_id: UUID
    report_date: date


# ============================================
# REPORT PHOTO SCHEMAS
# ============================================

class ReportPhotoBase(BaseModel):
    """Base report photo schema"""
    report_id: UUID
    photo_id: UUID


class ReportPhotoCreate(ReportPhotoBase):
    """Schema for creating a report photo association"""
    pass


class ReportPhotoResponse(ReportPhotoBase):
    """Schema for report photo response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# ANNOUNCEMENT SCHEMAS
# ============================================

class AnnouncementBase(BaseModel):
    """Base announcement schema"""
    title: str
    content: str
    announcement_date: date
    priority: str = "normal"  # low, normal, high, urgent
    is_active: bool = True


class AnnouncementCreate(AnnouncementBase):
    """Schema for creating an announcement"""
    pass


class AnnouncementUpdate(BaseModel):
    """Schema for updating an announcement"""
    title: Optional[str] = None
    content: Optional[str] = None
    announcement_date: Optional[date] = None
    priority: Optional[str] = None
    is_active: Optional[bool] = None


class AnnouncementResponse(AnnouncementBase):
    """Schema for announcement response"""
    id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# COMPLIANCE ALERT SCHEMAS
# ============================================

class ComplianceAlertBase(BaseModel):
    """Base compliance alert schema"""
    alert_type: str  # missing_immunization, expiring_credential, incomplete_form, late_pickup, etc
    entity_type: str  # child, staff, document
    entity_id: UUID
    description: str
    due_date: Optional[date] = None
    severity: str  # low, medium, high, critical
    is_resolved: bool = False
    resolved_at: Optional[datetime] = None


class ComplianceAlertCreate(ComplianceAlertBase):
    """Schema for creating a compliance alert"""
    pass


class ComplianceAlertUpdate(BaseModel):
    """Schema for updating a compliance alert"""
    description: Optional[str] = None
    due_date: Optional[date] = None
    severity: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolved_at: Optional[datetime] = None


class ComplianceAlertResponse(ComplianceAlertBase):
    """Schema for compliance alert response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
