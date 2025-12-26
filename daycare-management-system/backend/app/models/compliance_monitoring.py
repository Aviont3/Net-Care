# Compliance Monitoring Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel


class ComplianceAlert(BaseModel):
    """
    Automated compliance alerts for missing/expiring documents and violations.
    """
    __tablename__ = "compliance_alerts"

    alert_type = Column(String(100), nullable=False, index=True)  # missing_immunization, expiring_credential, incomplete_form, late_pickup, etc
    entity_type = Column(String(50), nullable=False, index=True)  # child, staff, document
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    description = Column(Text, nullable=False)
    due_date = Column(Date, index=True)
    severity = Column(String(20), nullable=False, index=True)  # low, medium, high, critical
    is_resolved = Column(Boolean, default=False, nullable=False, index=True)
    resolved_at = Column(DateTime)

    def __repr__(self):
        return f"<ComplianceAlert {self.alert_type} - {self.severity} for {self.entity_type} {self.entity_id}>"
