# Daily Operations Schemas
# ============================================

from datetime import date, datetime, time
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


# ============================================
# ATTENDANCE SCHEMAS
# ============================================

class AttendanceBase(BaseModel):
    """Base attendance schema"""
    child_id: UUID
    attendance_date: date
    check_in_time: time
    check_in_by_name: str
    check_in_signature_url: Optional[str] = None
    check_out_time: Optional[time] = None
    check_out_by_name: Optional[str] = None
    check_out_signature_url: Optional[str] = None
    is_late_pickup: bool = False
    late_pickup_minutes: int = 0
    notes: Optional[str] = None


class AttendanceCreate(BaseModel):
    """Schema for creating attendance (check-in)"""
    child_id: UUID
    check_in_time: time
    check_in_by_name: str
    check_in_signature_url: Optional[str] = None
    notes: Optional[str] = None


class AttendanceCheckOut(BaseModel):
    """Schema for checking out a child"""
    check_out_time: time
    check_out_by_name: str
    check_out_signature_url: Optional[str] = None
    notes: Optional[str] = None


class AttendanceResponse(AttendanceBase):
    """Schema for attendance response"""
    id: UUID
    recorded_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================
# ACTIVITY SCHEMAS
# ============================================

class ActivityBase(BaseModel):
    """Base activity schema"""
    child_id: UUID
    activity_date: date
    activity_time: datetime
    activity_type: str  # meal, nap, diaper, play, learning, outdoor
    activity_name: str
    description: Optional[str] = None
    mood: Optional[str] = None  # happy, sad, energetic, tired, cranky, neutral
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class ActivityCreate(ActivityBase):
    """Schema for creating an activity"""
    pass


class ActivityUpdate(BaseModel):
    """Schema for updating an activity"""
    activity_type: Optional[str] = None
    activity_name: Optional[str] = None
    description: Optional[str] = None
    mood: Optional[str] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None


class ActivityResponse(ActivityBase):
    """Schema for activity response"""
    id: UUID
    logged_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# PHOTO SCHEMAS
# ============================================

class PhotoBase(BaseModel):
    """Base photo schema"""
    photo_url: str
    photo_date: date
    photo_time: datetime
    caption: Optional[str] = None


class PhotoCreate(PhotoBase):
    """Schema for creating a photo"""
    child_ids: Optional[list[UUID]] = []  # List of children in the photo


class PhotoUpdate(BaseModel):
    """Schema for updating a photo"""
    caption: Optional[str] = None


class PhotoResponse(PhotoBase):
    """Schema for photo response"""
    id: UUID
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# CHILD PHOTO SCHEMAS
# ============================================

class ChildPhotoBase(BaseModel):
    """Base child photo schema"""
    photo_id: UUID
    child_id: UUID


class ChildPhotoCreate(ChildPhotoBase):
    """Schema for creating a child photo association"""
    pass


class ChildPhotoResponse(ChildPhotoBase):
    """Schema for child photo response"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
