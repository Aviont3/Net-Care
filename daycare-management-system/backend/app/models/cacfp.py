# CACFP (Child and Adult Care Food Program) Models
# ============================================

from sqlalchemy import Column, String, Date, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
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
