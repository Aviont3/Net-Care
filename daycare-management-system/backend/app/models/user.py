# User/Staff Model
# ============================================

from sqlalchemy import Column, String, Boolean, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class User(BaseModel):
    """
    Staff user accounts with role-based access control.
    """
    __tablename__ = "users"

    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, index=True)  # admin, staff
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    credentials = relationship("StaffCredential", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.email}>"