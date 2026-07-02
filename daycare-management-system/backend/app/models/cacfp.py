# CACFP (Child and Adult Care Food Program) Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Numeric
from app.models.base import BaseModel


class CACFPEligibility(BaseModel):
    """
    Tracks CACFP (Child and Adult Care Food Program) income eligibility
    determinations per child. Tier drives reimbursement rate:
      - free     → Tier I (income ≤ 130% FPL)
      - reduced  → Tier II (income 130–185% FPL)
      - paid     → above income threshold
    """
    __tablename__ = "cacfp_eligibility"

    child_id = Column(
        UUID(as_uuid=True),
        ForeignKey("children.id"),
        nullable=False,
        index=True,
    )
    eligibility_tier = Column(
        String(20),
        nullable=False,
        index=True,
    )  # free, reduced, paid
    determination_date = Column(Date, nullable=False)
    expiration_date = Column(Date, nullable=False)
    determination_method = Column(
        String(100),
        nullable=False,
    )  # e.g. "household_application", "categorical", "provider_household"
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    notes = Column(Text)

    # Relationships
    child = relationship("Child", backref="cacfp_eligibility_records")

    def __repr__(self):
        return (
            f"<CACFPEligibility child_id={self.child_id} "
            f"tier={self.eligibility_tier} active={self.is_active}>"
        )


class CACFPFoodItem(BaseModel):
    """Pre-categorized food items for quick meal logging."""
    __tablename__ = "cacfp_food_items"

    name = Column(String(200), nullable=False, index=True)
    component_category = Column(String(50), nullable=False)  # milk, meat_alternate, vegetable, fruit, grains
    sub_category = Column(String(50))  # dark_green, red_orange, starchy, whole_grain_rich, etc.
    serving_description = Column(String(200))  # "1/2 cup", "1 oz eq"
    is_whole_grain_rich = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, nullable=False)

    def __repr__(self):
        return f"<CACFPFoodItem {self.name} ({self.component_category})>"


class CACFPMonthlyClaim(BaseModel):
    """Monthly reimbursement claim for WINS submission."""
    __tablename__ = "cacfp_monthly_claims"

    claim_month = Column(Integer, nullable=False)  # 1-12
    claim_year = Column(Integer, nullable=False)
    operating_days = Column(Integer, nullable=False)
    total_attendance = Column(Integer, nullable=False)

    # Meal counts
    breakfast_count = Column(Integer, default=0, nullable=False)
    lunch_count = Column(Integer, default=0, nullable=False)
    supper_count = Column(Integer, default=0, nullable=False)
    snack_count = Column(Integer, default=0, nullable=False)

    # Enrollment by tier
    free_enrolled = Column(Integer, default=0, nullable=False)
    reduced_enrolled = Column(Integer, default=0, nullable=False)
    paid_enrolled = Column(Integer, default=0, nullable=False)

    # Calculated reimbursement
    total_reimbursement = Column(Numeric(10, 2))

    # Status
    status = Column(String(20), default="draft", nullable=False, index=True)  # draft, submitted, approved
    submitted_at = Column(DateTime)
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    notes = Column(Text)

    # Relationships
    submitter = relationship("User", foreign_keys=[submitted_by])

    def __repr__(self):
        return f"<CACFPMonthlyClaim {self.claim_year}-{self.claim_month:02d} status={self.status}>"


class CACFPAuditLog(BaseModel):
    """
    Immutable audit trail for all CACFP-related record changes.
    Rows in this table are never updated or deleted — only inserted.
    Required for USDA CACFP 3-year record retention / audit defense.
    """
    __tablename__ = "cacfp_audit_log"

    action = Column(
        String(50), nullable=False, index=True
    )  # create, correction, verify, submit_claim, deactivate
    entity_type = Column(
        String(50), nullable=False, index=True
    )  # meal_activity, eligibility, claim
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    field_changed = Column(String(100))   # which field was corrected (None for creates)
    old_value = Column(Text)
    new_value = Column(Text)
    reason = Column(Text)                 # required for corrections

    performed_by = Column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )

    # Relationships
    performer = relationship("User", foreign_keys=[performed_by])

    def __repr__(self):
        return (
            f"<CACFPAuditLog action={self.action} entity={self.entity_type}"
            f"/{self.entity_id} by={self.performed_by}>"
        )
