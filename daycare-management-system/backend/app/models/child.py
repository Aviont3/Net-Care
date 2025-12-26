# Children & Family Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Child(BaseModel):
    """
    Core child profiles with medical and allergy information.
    """
    __tablename__ = "children"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20))
    allergies = Column(Text)
    dietary_restrictions = Column(Text)
    medical_conditions = Column(Text)
    special_needs = Column(Text)
    photo_url = Column(String(500))
    enrollment_date = Column(Date, nullable=False)
    withdrawal_date = Column(Date)
    is_active = Column(Boolean, default=True, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])
    parents = relationship("ChildParent", back_populates="child", cascade="all, delete-orphan")
    emergency_contacts = relationship("EmergencyContact", back_populates="child", cascade="all, delete-orphan")
    authorized_pickups = relationship("AuthorizedPickup", back_populates="child", cascade="all, delete-orphan")
    enrollment_form = relationship("EnrollmentForm", back_populates="child", uselist=False, cascade="all, delete-orphan")
    immunization_records = relationship("ImmunizationRecord", back_populates="child", cascade="all, delete-orphan")
    attendance_records = relationship("Attendance", back_populates="child", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="child", cascade="all, delete-orphan")
    child_photos = relationship("ChildPhoto", back_populates="child", cascade="all, delete-orphan")
    incident_reports = relationship("IncidentReport", back_populates="child", cascade="all, delete-orphan")
    medication_authorizations = relationship("MedicationAuthorization", back_populates="child", cascade="all, delete-orphan")
    medication_logs = relationship("MedicationLog", back_populates="child", cascade="all, delete-orphan")
    daily_reports = relationship("DailyReport", back_populates="child", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Child {self.first_name} {self.last_name}>"


class Parent(BaseModel):
    """
    Parent and guardian contact information.
    """
    __tablename__ = "parents"

    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), index=True)
    phone_primary = Column(String(20), nullable=False, index=True)
    phone_secondary = Column(String(20))
    address_street = Column(String(255))
    address_city = Column(String(100))
    address_state = Column(String(2))
    address_zip = Column(String(10))
    employer = Column(String(255))
    work_phone = Column(String(20))
    is_primary_contact = Column(Boolean, default=False, nullable=False)

    # Relationships
    children = relationship("ChildParent", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Parent {self.first_name} {self.last_name}>"


class ChildParent(BaseModel):
    """
    Many-to-many relationship between children and parents/guardians.
    """
    __tablename__ = "child_parents"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("parents.id"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)  # mother, father, guardian, grandparent, etc
    is_primary = Column(Boolean, default=False, nullable=False)
    has_custody = Column(Boolean, default=True, nullable=False)
    can_pickup = Column(Boolean, default=True, nullable=False)

    # Relationships
    child = relationship("Child", back_populates="parents")
    parent = relationship("Parent", back_populates="children")

    def __repr__(self):
        return f"<ChildParent child_id={self.child_id} parent_id={self.parent_id}>"


class EmergencyContact(BaseModel):
    """
    DCFS requires minimum 2 emergency contacts per child.
    """
    __tablename__ = "emergency_contacts"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    phone_primary = Column(String(20), nullable=False)
    phone_secondary = Column(String(20))
    priority_order = Column(Integer, nullable=False)  # Order to contact (1, 2, 3, etc)
    notes = Column(Text)

    # Relationships
    child = relationship("Child", back_populates="emergency_contacts")

    def __repr__(self):
        return f"<EmergencyContact {self.name} for child_id={self.child_id}>"


class AuthorizedPickup(BaseModel):
    """
    List of people authorized to pick up each child with photo verification.
    """
    __tablename__ = "authorized_pickup"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    relationship_type = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    photo_url = Column(String(500))
    identification_notes = Column(Text)
    requires_password = Column(Boolean, default=False, nullable=False)
    password_hint = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    child = relationship("Child", back_populates="authorized_pickups")

    def __repr__(self):
        return f"<AuthorizedPickup {self.name} for child_id={self.child_id}>"
