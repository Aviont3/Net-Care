# Authorized Pickup Management Endpoints
# ============================================

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.child import AuthorizedPickup, Child
from app.models.user import User
from app.schemas.child import (
    AuthorizedPickupCreate,
    AuthorizedPickupUpdate,
    AuthorizedPickupResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=AuthorizedPickupResponse, status_code=status.HTTP_201_CREATED)
async def create_authorized_pickup(
    pickup_data: AuthorizedPickupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a person to the authorized pickup list for a child.
    Includes photo verification capability for enhanced security.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == pickup_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {pickup_data.child_id} not found"
        )

    new_pickup = AuthorizedPickup(**pickup_data.model_dump())

    db.add(new_pickup)
    db.commit()
    db.refresh(new_pickup)

    return new_pickup


@router.get("/child/{child_id}", response_model=List[AuthorizedPickupResponse])
async def get_child_authorized_pickups(
    child_id: UUID,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all authorized pickup persons for a specific child.
    Optionally filter by active status.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(AuthorizedPickup).filter(AuthorizedPickup.child_id == child_id)

    if is_active is not None:
        query = query.filter(AuthorizedPickup.is_active == is_active)

    pickups = query.order_by(AuthorizedPickup.name).all()

    return pickups


@router.get("/active", response_model=List[AuthorizedPickupResponse])
async def get_all_active_authorized_pickups(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active authorized pickup persons across all children.
    Useful for quick lookup during pickup time.
    """
    offset = (page - 1) * page_size

    pickups = db.query(AuthorizedPickup)\
        .filter(AuthorizedPickup.is_active == True)\
        .order_by(AuthorizedPickup.name)\
        .offset(offset)\
        .limit(page_size)\
        .all()

    return pickups


@router.get("/{pickup_id}", response_model=AuthorizedPickupResponse)
async def get_authorized_pickup(
    pickup_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific authorized pickup person by ID.
    """
    pickup = db.query(AuthorizedPickup).filter(AuthorizedPickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authorized pickup with ID {pickup_id} not found"
        )

    return pickup


@router.put("/{pickup_id}", response_model=AuthorizedPickupResponse)
async def update_authorized_pickup(
    pickup_id: UUID,
    pickup_data: AuthorizedPickupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an authorized pickup person's information.
    Can update contact info, photo, password requirements, etc.
    """
    pickup = db.query(AuthorizedPickup).filter(AuthorizedPickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authorized pickup with ID {pickup_id} not found"
        )

    # Update only provided fields
    update_data = pickup_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(pickup, field, value)

    db.commit()
    db.refresh(pickup)

    return pickup


@router.patch("/{pickup_id}/deactivate", response_model=AuthorizedPickupResponse)
async def deactivate_authorized_pickup(
    pickup_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate an authorized pickup person (soft delete).
    Recommended over hard delete for audit trail.
    """
    pickup = db.query(AuthorizedPickup).filter(AuthorizedPickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authorized pickup with ID {pickup_id} not found"
        )

    pickup.is_active = False
    db.commit()
    db.refresh(pickup)

    return pickup


@router.patch("/{pickup_id}/activate", response_model=AuthorizedPickupResponse)
async def activate_authorized_pickup(
    pickup_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reactivate an authorized pickup person.
    """
    pickup = db.query(AuthorizedPickup).filter(AuthorizedPickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authorized pickup with ID {pickup_id} not found"
        )

    pickup.is_active = True
    db.commit()
    db.refresh(pickup)

    return pickup


@router.delete("/{pickup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_authorized_pickup(
    pickup_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an authorized pickup person (hard delete).
    Only admins can perform hard deletes.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can permanently delete authorized pickup persons"
        )

    pickup = db.query(AuthorizedPickup).filter(AuthorizedPickup.id == pickup_id).first()

    if not pickup:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authorized pickup with ID {pickup_id} not found"
        )

    db.delete(pickup)
    db.commit()

    return None


@router.get("/search/by-name", response_model=List[AuthorizedPickupResponse])
async def search_authorized_pickups_by_name(
    name: str = Query(..., min_length=2, description="Search by name (minimum 2 characters)"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Search authorized pickup persons by name.
    Useful during pickup time to quickly find and verify authorization.
    """
    search_filter = f"%{name}%"

    pickups = db.query(AuthorizedPickup)\
        .filter(
            AuthorizedPickup.name.ilike(search_filter),
            AuthorizedPickup.is_active == is_active
        )\
        .order_by(AuthorizedPickup.name)\
        .all()

    return pickups


@router.get("/verify/{child_id}/{pickup_name}")
async def verify_pickup_authorization(
    child_id: UUID,
    pickup_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify if a person is authorized to pick up a specific child.
    Returns authorization details including photo, password requirements, etc.

    Use this endpoint during pickup to quickly verify authorization.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    # Search for active authorized pickup
    search_filter = f"%{pickup_name}%"
    pickup = db.query(AuthorizedPickup)\
        .filter(
            AuthorizedPickup.child_id == child_id,
            AuthorizedPickup.name.ilike(search_filter),
            AuthorizedPickup.is_active == True
        )\
        .first()

    if not pickup:
        return {
            "authorized": False,
            "child_id": str(child_id),
            "child_name": f"{child.first_name} {child.last_name}",
            "pickup_name": pickup_name,
            "message": "This person is NOT authorized to pick up this child"
        }

    return {
        "authorized": True,
        "child_id": str(child_id),
        "child_name": f"{child.first_name} {child.last_name}",
        "pickup_person": {
            "id": str(pickup.id),
            "name": pickup.name,
            "relationship_type": pickup.relationship_type,
            "phone": pickup.phone,
            "photo_url": pickup.photo_url,
            "requires_password": pickup.requires_password,
            "password_hint": pickup.password_hint if pickup.requires_password else None,
            "identification_notes": pickup.identification_notes
        },
        "message": "This person IS authorized to pick up this child"
    }


@router.get("/photo-verification-required", response_model=List[AuthorizedPickupResponse])
async def get_pickups_requiring_photo_verification(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active authorized pickups that don't have a photo uploaded.
    Used for compliance and security improvement.
    """
    pickups = db.query(AuthorizedPickup)\
        .filter(
            AuthorizedPickup.is_active == True,
            AuthorizedPickup.photo_url.is_(None)
        )\
        .order_by(AuthorizedPickup.created_at.desc())\
        .all()

    return pickups
