# CACFP (Child and Adult Care Food Program) Endpoints
# ============================================

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cacfp import CACFPEligibility
from app.models.child import Child
from app.models.user import User
from app.schemas.cacfp import (
    CACFPEligibilityCreate,
    CACFPEligibilityResponse,
    CACFPEligibilityUpdate,
)
from app.core.security import get_current_user

router = APIRouter()

_VALID_TIERS = {"free", "reduced", "paid"}


@router.post("/", response_model=CACFPEligibilityResponse, status_code=status.HTTP_201_CREATED)
async def create_eligibility(
    data: CACFPEligibilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a CACFP eligibility record for a child.
    Automatically deactivates any existing active record for that child
    so only one active record exists at a time.
    """
    if data.eligibility_tier not in _VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"eligibility_tier must be one of: {', '.join(sorted(_VALID_TIERS))}",
        )

    if data.expiration_date <= data.determination_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expiration_date must be after determination_date",
        )

    # Verify child exists
    child = db.query(Child).filter(Child.id == data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {data.child_id} not found",
        )

    # Deactivate any existing active records for this child
    db.query(CACFPEligibility).filter(
        CACFPEligibility.child_id == data.child_id,
        CACFPEligibility.is_active == True,  # noqa: E712
    ).update({"is_active": False})

    record = CACFPEligibility(**data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@router.get("/", response_model=List[CACFPEligibilityResponse])
async def list_eligibility(
    child_id: Optional[UUID] = Query(None, description="Filter by child ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List CACFP eligibility records.
    Optionally filter by child_id and/or is_active.
    """
    query = db.query(CACFPEligibility)

    if child_id is not None:
        query = query.filter(CACFPEligibility.child_id == child_id)

    if is_active is not None:
        query = query.filter(CACFPEligibility.is_active == is_active)

    return query.order_by(CACFPEligibility.determination_date.desc()).all()


@router.get("/child/{child_id}", response_model=CACFPEligibilityResponse)
async def get_active_eligibility_for_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the active CACFP eligibility record for a specific child.
    Returns 404 if no active record exists.
    """
    record = (
        db.query(CACFPEligibility)
        .filter(
            CACFPEligibility.child_id == child_id,
            CACFPEligibility.is_active == True,  # noqa: E712
        )
        .first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active CACFP eligibility record found for child {child_id}",
        )

    return record


@router.put("/{eligibility_id}", response_model=CACFPEligibilityResponse)
async def update_eligibility(
    eligibility_id: UUID,
    data: CACFPEligibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update a CACFP eligibility record.
    Only updates fields that are provided.
    """
    record = db.query(CACFPEligibility).filter(CACFPEligibility.id == eligibility_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CACFP eligibility record {eligibility_id} not found",
        )

    if data.eligibility_tier is not None and data.eligibility_tier not in _VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"eligibility_tier must be one of: {', '.join(sorted(_VALID_TIERS))}",
        )

    update_fields = data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record
