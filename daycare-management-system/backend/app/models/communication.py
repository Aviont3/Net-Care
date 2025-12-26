# Parent Communication Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class DailyReport(BaseModel):
    """
    AI-generated daily reports sent to parents via email.
    """
    __tablename__ = "daily_reports"

    child_id = Column(UUID(as_uuid=True), ForeignKey("children.id"), nullable=False, index=True)
    report_date = Column(Date, nullable=False, index=True)
    ai_generated_summary = Column(Text)  # GPT-4 generated narrative summary
    custom_notes = Column(Text)  # Staff can add additional notes
    overall_mood = Column(String(50))
    sent_to_parents = Column(Boolean, default=False, nullable=False, index=True)
    sent_at = Column(DateTime)
    activities_summary = Column(JSON)  # Quick stats: meal count, nap duration, etc
    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Relationships
    child = relationship("Child", back_populates="daily_reports")
    generator = relationship("User", foreign_keys=[generated_by])
    report_photos = relationship("ReportPhoto", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DailyReport for child_id={self.child_id} on {self.report_date}>"


class ReportPhoto(BaseModel):
    """
    Many-to-many: Photos included in daily reports.
    """
    __tablename__ = "report_photos"

    report_id = Column(UUID(as_uuid=True), ForeignKey("daily_reports.id"), nullable=False, index=True)
    photo_id = Column(UUID(as_uuid=True), ForeignKey("photos.id"), nullable=False, index=True)

    # Relationships
    report = relationship("DailyReport", back_populates="report_photos")
    photo = relationship("Photo", back_populates="report_photos")

    def __repr__(self):
        return f"<ReportPhoto report_id={self.report_id} photo_id={self.photo_id}>"


class Announcement(BaseModel):
    """
    Broadcast announcements to all parents (closures, events, etc).
    """
    __tablename__ = "announcements"

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    announcement_date = Column(Date, nullable=False, index=True)
    priority = Column(String(20), default="normal", nullable=False, index=True)  # low, normal, high, urgent
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self):
        return f"<Announcement {self.title} on {self.announcement_date}>"
