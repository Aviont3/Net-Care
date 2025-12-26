# Children & Family Schemas
# ============================================

from datetime import date
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator


# ============================================
# CHILD SCHEMAS
# ============================================

class ChildBase(BaseModel):
    """Base child schema with common fields"""
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    allergies: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    medical_conditions: Optional[str] = None
    special_needs: Optional[str] = None
    photo_url: Optional[str] = None
    enrollment_date: date
    withdrawal_date: Optional[date] = None
    is_active: bool = True


class ChildCreate(ChildBase):
    """Schema for creating a new child"""
    pass


class ChildUpdate(BaseModel):
    """Schema for updating a child (all fields optional)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    allergies: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    medical_conditions: Optional[str] = None
    special_needs: Optional[str] = None
    photo_url: Optional[str] = None
    enrollment_date: Optional[date] = None
    withdrawal_date: Optional[date] = None
    is_active: Optional[bool] = None


class ChildResponse(ChildBase):
    """Schema for child response"""
    id: UUID
    created_by: Optional[UUID] = None
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


class ChildListResponse(BaseModel):
    """Schema for paginated child list"""
    children: List[ChildResponse]
    total: int
    page: int
    page_size: int


# ============================================
# PARENT SCHEMAS
# ============================================

class ParentBase(BaseModel):
    """Base parent schema with common fields"""
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_primary: str
    phone_secondary: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    employer: Optional[str] = None
    work_phone: Optional[str] = None
    is_primary_contact: bool = False


class ParentCreate(ParentBase):
    """Schema for creating a new parent"""
    pass


class ParentUpdate(BaseModel):
    """Schema for updating a parent (all fields optional)"""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    employer: Optional[str] = None
    work_phone: Optional[str] = None
    is_primary_contact: Optional[bool] = None


class ParentResponse(ParentBase):
    """Schema for parent response"""
    id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# ============================================
# CHILD-PARENT RELATIONSHIP SCHEMAS
# ============================================

class ChildParentBase(BaseModel):
    """Base child-parent relationship schema"""
    child_id: UUID
    parent_id: UUID
    relationship_type: str  # mother, father, guardian, grandparent, etc
    is_primary: bool = False
    has_custody: bool = True
    can_pickup: bool = True


class ChildParentCreate(ChildParentBase):
    """Schema for creating a child-parent relationship"""
    pass


class ChildParentUpdate(BaseModel):
    """Schema for updating a child-parent relationship"""
    relationship_type: Optional[str] = None
    is_primary: Optional[bool] = None
    has_custody: Optional[bool] = None
    can_pickup: Optional[bool] = None


class ChildParentResponse(ChildParentBase):
    """Schema for child-parent relationship response"""
    id: UUID
    created_at: date

    class Config:
        from_attributes = True


# ============================================
# EMERGENCY CONTACT SCHEMAS
# ============================================

class EmergencyContactBase(BaseModel):
    """Base emergency contact schema"""
    child_id: UUID
    name: str
    relationship_type: str
    phone_primary: str
    phone_secondary: Optional[str] = None
    priority_order: int
    notes: Optional[str] = None


class EmergencyContactCreate(EmergencyContactBase):
    """Schema for creating an emergency contact"""
    pass


class EmergencyContactUpdate(BaseModel):
    """Schema for updating an emergency contact"""
    name: Optional[str] = None
    relationship_type: Optional[str] = None
    phone_primary: Optional[str] = None
    phone_secondary: Optional[str] = None
    priority_order: Optional[int] = None
    notes: Optional[str] = None


class EmergencyContactResponse(EmergencyContactBase):
    """Schema for emergency contact response"""
    id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True


# ============================================
# AUTHORIZED PICKUP SCHEMAS
# ============================================

class AuthorizedPickupBase(BaseModel):
    """Base authorized pickup schema"""
    child_id: UUID
    name: str
    relationship_type: str
    phone: str
    photo_url: Optional[str] = None
    identification_notes: Optional[str] = None
    requires_password: bool = False
    password_hint: Optional[str] = None
    is_active: bool = True


class AuthorizedPickupCreate(AuthorizedPickupBase):
    """Schema for creating an authorized pickup"""
    pass


class AuthorizedPickupUpdate(BaseModel):
    """Schema for updating an authorized pickup"""
    name: Optional[str] = None
    relationship_type: Optional[str] = None
    phone: Optional[str] = None
    photo_url: Optional[str] = None
    identification_notes: Optional[str] = None
    requires_password: Optional[bool] = None
    password_hint: Optional[str] = None
    is_active: Optional[bool] = None


class AuthorizedPickupResponse(AuthorizedPickupBase):
    """Schema for authorized pickup response"""
    id: UUID
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True
