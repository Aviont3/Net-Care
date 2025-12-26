# Children Management Endpoints
# ============================================

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.child import Child
from app.models.user import User
from app.schemas.child import (
    ChildCreate,
    ChildUpdate,
    ChildResponse,
    ChildListResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    child_data: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new child profile.
    Only accessible by authenticated staff.
    """
    new_child = Child(
        **child_data.model_dump(),
        created_by=current_user.id
    )

    db.add(new_child)
    db.commit()
    db.refresh(new_child)

    return new_child


@router.get("/", response_model=ChildListResponse)
async def get_children(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of children.
    Supports search and filtering.
    """
    query = db.query(Child)

    # Apply filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Child.first_name.ilike(search_filter),
                Child.last_name.ilike(search_filter)
            )
        )

    if is_active is not None:
        query = query.filter(Child.is_active == is_active)

    # Get total count
    total = query.count()

    # Apply pagination
    offset = (page - 1) * page_size
    children = query.order_by(Child.last_name, Child.first_name)\
                    .offset(offset)\
                    .limit(page_size)\
                    .all()

    return {
        "children": children,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific child by ID.
    """
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    return child


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: UUID,
    child_data: ChildUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a child's information.
    Only updates fields that are provided.
    """
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    # Update only provided fields
    update_data = child_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(child, field, value)

    db.commit()
    db.refresh(child)

    return child


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a child profile.
    Note: This is a hard delete. Consider soft delete (setting is_active=False) instead.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete child profiles"
        )

    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    db.delete(child)
    db.commit()

    return None


@router.patch("/{child_id}/deactivate", response_model=ChildResponse)
async def deactivate_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a child (soft delete).
    Recommended over hard delete for record keeping.
    """
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    child.is_active = False
    db.commit()
    db.refresh(child)

    return child


@router.patch("/{child_id}/activate", response_model=ChildResponse)
async def activate_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reactivate a child.
    """
    child = db.query(Child).filter(Child.id == child_id).first()

    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    child.is_active = True
    db.commit()
    db.refresh(child)

    return child
