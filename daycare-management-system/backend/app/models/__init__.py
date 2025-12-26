# Models Package Initialization
# ============================================

from app.models.base import BaseModel
from app.models.user import User

# Children & Family Models
from app.models.child import (
    Child,
    Parent,
    ChildParent,
    EmergencyContact,
    AuthorizedPickup,
)

# DCFS Compliance Models
from app.models.compliance import (
    EnrollmentForm,
    ImmunizationRecord,
    StaffCredential,
)

# Daily Operations Models
from app.models.daily_operations import (
    Attendance,
    Activity,
    Photo,
    ChildPhoto,
)

# Health & Safety Models
from app.models.health_safety import (
    IncidentReport,
    MedicationAuthorization,
    MedicationLog,
)

# Parent Communication Models
from app.models.communication import (
    DailyReport,
    ReportPhoto,
    Announcement,
)

# Compliance Monitoring Models
from app.models.compliance_monitoring import ComplianceAlert

__all__ = [
    "BaseModel",
    "User",
    # Children & Family
    "Child",
    "Parent",
    "ChildParent",
    "EmergencyContact",
    "AuthorizedPickup",
    # DCFS Compliance
    "EnrollmentForm",
    "ImmunizationRecord",
    "StaffCredential",
    # Daily Operations
    "Attendance",
    "Activity",
    "Photo",
    "ChildPhoto",
    # Health & Safety
    "IncidentReport",
    "MedicationAuthorization",
    "MedicationLog",
    # Parent Communication
    "DailyReport",
    "ReportPhoto",
    "Announcement",
    # Compliance Monitoring
    "ComplianceAlert",
]