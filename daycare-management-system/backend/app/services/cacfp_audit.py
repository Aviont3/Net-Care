"""
CACFP Audit Trail Service
==========================
Creates immutable audit log entries for CACFP-related record changes.

USDA regulations (7 CFR 226) require:
  - Point-of-service meal records must be retained 3 years + current year
  - All corrections must be documented with the original value, corrected value,
    date, and identity of the person making the correction
  - Records must not be destroyed prior to audit resolution

Usage:
    from app.services.cacfp_audit import log_audit

    log_audit(
        db, "create", "meal_activity", new_activity.id, current_user.id
    )
    db.commit()   # caller controls the transaction boundary
"""
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.cacfp import CACFPAuditLog


def log_audit(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: UUID,
    performed_by: UUID,
    *,
    field_changed: Optional[str] = None,
    old_value: Optional[str] = None,
    new_value: Optional[str] = None,
    reason: Optional[str] = None,
) -> CACFPAuditLog:
    """
    Stage an immutable audit log entry in the current session.

    The entry is added to the session but NOT committed — the caller is
    responsible for committing (or rolling back) the enclosing transaction.
    This keeps audit entries atomic with the business operation they describe.

    Args:
        db:            Active SQLAlchemy session.
        action:        One of: create, correction, verify, submit_claim, deactivate.
        entity_type:   One of: meal_activity, eligibility, claim.
        entity_id:     UUID of the affected record.
        performed_by:  UUID of the user who performed the action.
        field_changed: Name of the field that was corrected (corrections only).
        old_value:     Previous value as a string (corrections only).
        new_value:     Updated value as a string (corrections only).
        reason:        Required for correction actions; explains why the change
                       was made (stored verbatim for auditor review).

    Returns:
        The (unsaved) CACFPAuditLog ORM instance.
    """
    entry = CACFPAuditLog(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        performed_by=performed_by,
        field_changed=field_changed,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
    )
    db.add(entry)
    return entry
