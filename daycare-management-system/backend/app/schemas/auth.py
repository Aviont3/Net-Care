# Authentication Schemas (Request/Response)
# ============================================

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_serializer


class Token(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Token refresh request schema"""
    refresh_token: str


class ParentActivateRequest(BaseModel):
    """Parent account activation request"""
    invite_code: str
    password: str


class TokenData(BaseModel):
    """Token payload data"""
    email: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request schema"""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: str = "staff"


class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool

    @field_serializer('id')
    def serialize_id(self, value: UUID) -> str:
        return str(value)

    class Config:
        from_attributes = True
