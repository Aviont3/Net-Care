# DCFS Compliance Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class EnrollmentForm(BaseModel):
    """
    DCFS Form 602 - Child Enrollment Record with electronic signatures.
    """
    __tablename__ = "enrollment_forms"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, unique=True, index=True)
    enrollment_date = Column(Date, nullable=False, index=True)
    parent_signature_url = Column(String(500))
    parent_signed_at = Column(DateTime)
    staff_signature_url = Column(String(500))
    staff_signed_at = Column(DateTime)
    form_data = Column(JSON)  # Complete DCFS Form 602 data in JSON format
    is_complete = Column(Boolean, default=False, nullable=False, index=True)
    completed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    child = relationship("Child", back_populates="enrollment_form")
    completed_by_user = relationship("User", foreign_keys=[completed_by])

    def __repr__(self):
        return f"<EnrollmentForm child_id={self.child_id} complete={self.is_complete}>"


class ImmunizationRecord(BaseModel):
    """
    Vaccination records with expiration tracking for DCFS compliance.
    """
    __tablename__ = "immunization_records"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    vaccine_name = Column(String(255), nullable=False, index=True)
    administration_date = Column(Date, nullable=False)
    expiration_date = Column(Date, index=True)
    document_url = Column(String(500))
    provider_name = Column(String(255))
    notes = Column(Text)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Relationships
    child = relationship("Child", back_populates="immunization_records")

    def __repr__(self):
        return f"<ImmunizationRecord {self.vaccine_name} for child_id={self.child_id}>"


class StaffCredential(BaseModel):
    """
    Staff certifications and credentials required by DCFS (CPR, First Aid, etc).
    """
    __tablename__ = "staff_credentials"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    credential_type = Column(String(100), nullable=False, index=True)  # CPR, First Aid, Background Check, TB Test, DCFS Training
    credential_number = Column(String(100))
    issue_date = Column(Date, nullable=False)
    expiration_date = Column(Date, index=True)
    document_url = Column(String(500))
    is_verified = Column(Boolean, default=False, nullable=False)
    is_expired = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    user = relationship("User", back_populates="credentials")

    def __repr__(self):
        return f"<StaffCredential {self.credential_type} for user_id={self.user_id}>"
