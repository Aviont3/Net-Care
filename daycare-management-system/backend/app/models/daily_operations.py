# Daily Operations Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, Integer, Time, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Attendance(BaseModel):
    """
    Daily attendance tracking with electronic signatures for DCFS compliance.
    """
    __tablename__ = "attendance"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    attendance_date = Column(Date, nullable=False, index=True)
    check_in_time = Column(Time, nullable=False)
    check_in_by_name = Column(String(255), nullable=False)  # Parent/guardian name
    check_in_signature_url = Column(String(500))
    check_out_time = Column(Time)
    check_out_by_name = Column(String(255))
    check_out_signature_url = Column(String(500))
    is_late_pickup = Column(Boolean, default=False, nullable=False)
    late_pickup_minutes = Column(Integer, default=0, nullable=False)
    notes = Column(Text)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    child = relationship("Child", back_populates="attendance_records")
    recorder = relationship("User", foreign_keys=[recorded_by])

    def __repr__(self):
        return f"<Attendance child_id={self.child_id} date={self.attendance_date}>"


class Activity(BaseModel):
    """
    Daily activity logs (meals, naps, diaper changes) used for AI report generation.
    """
    __tablename__ = "activities"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    activity_date = Column(Date, nullable=False, index=True)
    activity_time = Column(DateTime, nullable=False)
    activity_type = Column(String(50), nullable=False, index=True)  # meal, nap, diaper, play, learning, outdoor
    activity_name = Column(String(255), nullable=False)
    description = Column(Text)
    mood = Column(String(50))  # happy, sad, energetic, tired, cranky, neutral
    duration_minutes = Column(Integer)
    notes = Column(Text)
    logged_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    child = relationship("Child", back_populates="activities")
    logger = relationship("User", foreign_keys=[logged_by])

    def __repr__(self):
        return f"<Activity {self.activity_type} for child_id={self.child_id} on {self.activity_date}>"


class Photo(BaseModel):
    """
    Photo storage with metadata for daily reports and documentation.
    """
    __tablename__ = "photos"

    photo_url = Column(String(500), nullable=False)
    photo_date = Column(Date, nullable=False, index=True)
    photo_time = Column(DateTime, nullable=False)
    caption = Column(Text)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    # Relationships
    uploader = relationship("User", foreign_keys=[uploaded_by])
    child_photos = relationship("ChildPhoto", back_populates="photo", cascade="all, delete-orphan")
    report_photos = relationship("ReportPhoto", back_populates="photo", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Photo {self.photo_url} uploaded on {self.photo_date}>"


class ChildPhoto(BaseModel):
    """
    Many-to-many: One photo can contain multiple children.
    """
    __tablename__ = "child_photos"

    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id"), nullable=False, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)

    # Relationships
    photo = relationship("Photo", back_populates="child_photos")
    child = relationship("Child", back_populates="child_photos")

    def __repr__(self):
        return f"<ChildPhoto photo_id={self.photo_id} child_id={self.child_id}>"
