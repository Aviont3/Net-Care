# Health & Safety Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, Time, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class IncidentReport(BaseModel):
    """
    DCFS Form 337 - Incident and Accident Reports with required notifications.
    """
    __tablename__ = "incident_reports"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    incident_date = Column(Date, nullable=False, index=True)
    incident_time = Column(Time, nullable=False)
    incident_type = Column(String(50), nullable=False, index=True)  # injury, illness, behavioral, accident, other
    description = Column(Text, nullable=False)
    circumstances = Column(Text, nullable=False)
    injury_description = Column(Text)
    body_part_affected = Column(String(100))
    action_taken = Column(Text, nullable=False)
    witnesses = Column(Text)
    photo_url = Column(String(500))
    parent_notified = Column(Boolean, default=False, nullable=False)
    parent_notified_at = Column(DateTime)
    parent_notification_method = Column(String(50))  # phone, email, in-person, sms
    dcfs_notification_required = Column(Boolean, default=False, nullable=False, index=True)
    dcfs_notified_at = Column(DateTime)
    staff_signature_url = Column(String(500))
    staff_signed_at = Column(DateTime)
    reported_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    child = relationship("Child", back_populates="incident_reports")
    reporter = relationship("User", foreign_keys=[reported_by])

    def __repr__(self):
        return f"<IncidentReport {self.incident_type} for child_id={self.child_id} on {self.incident_date}>"


class MedicationAuthorization(BaseModel):
    """
    Parent authorization for medication administration - DCFS required.
    """
    __tablename__ = "medication_authorizations"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    medication_name = Column(String(255), nullable=False)
    dosage = Column(String(100), nullable=False)
    frequency = Column(String(100), nullable=False)  # once daily, twice daily, as needed, etc
    administration_instructions = Column(Text, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, index=True)
    prescribing_doctor = Column(String(255))
    parent_signature_url = Column(String(500))
    parent_signed_at = Column(DateTime)
    is_active = Column(Boolean, default=True, nullable=False, index=True)

    # Relationships
    child = relationship("Child", back_populates="medication_authorizations")
    medication_logs = relationship("MedicationLog", back_populates="authorization", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<MedicationAuthorization {self.medication_name} for child_id={self.child_id}>"


class MedicationLog(BaseModel):
    """
    Log of actual medication administration with staff signatures.
    """
    __tablename__ = "medication_logs"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    authorization_id = Column(UUID(as_uuid=True), ForeignKey("medication_authorizations.id"), nullable=False, index=True)
    administration_date = Column(Date, nullable=False, index=True)
    administration_time = Column(Time, nullable=False)
    dosage_given = Column(String(100), nullable=False)
    staff_signature_url = Column(String(500))
    administered_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    notes = Column(Text)
    parent_notified = Column(Boolean, default=False, nullable=False)

    # Relationships
    child = relationship("Child", back_populates="medication_logs")
    authorization = relationship("MedicationAuthorization", back_populates="medication_logs")
    administrator = relationship("User", foreign_keys=[administered_by])

    def __repr__(self):
        return f"<MedicationLog for child_id={self.child_id} on {self.administration_date}>"
