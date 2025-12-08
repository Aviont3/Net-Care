# User/Staff Model
# ============================================

from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel


class User(BaseModel):
    """
    Staff user accounts for Netta's Bounce Around Daycare.
    Currently 2 staff members (Netta + 1 other).
    """
    __tablename__ = "users"
    
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="staff")  # admin, staff
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User {self.email}>"