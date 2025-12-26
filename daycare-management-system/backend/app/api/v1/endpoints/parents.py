# Parents Management Endpoints
# ============================================

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.child import Parent, ChildParent, Child
from app.models.user import User
from app.schemas.child import (
    ParentCreate,
    ParentUpdate,
    ParentResponse,
    ChildParentCreate,
    ChildParentUpdate,
    ChildParentResponse,
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================
# PARENT ENDPOINTS
# ============================================

@router.post("/", response_model=ParentResponse, status_code=status.HTTP_201_CREATED)
async def create_parent(
    parent_data: ParentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new parent/guardian profile.
    Only accessible by authenticated staff.
    """
    new_parent = Parent(**parent_data.model_dump())

    db.add(new_parent)
    db.commit()
    db.refresh(new_parent)

    return new_parent


@router.get("/", response_model=List[ParentResponse])
async def get_parents(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by name, email, or phone"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get paginated list of parents.
    Supports search by name, email, or phone.
    """
    query = db.query(Parent)

    # Apply search filter
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Parent.first_name.ilike(search_filter),
                Parent.last_name.ilike(search_filter),
                Parent.email.ilike(search_filter),
                Parent.phone_primary.ilike(search_filter)
            )
        )

    # Apply pagination
    offset = (page - 1) * page_size
    parents = query.order_by(Parent.last_name, Parent.first_name)\
                   .offset(offset)\
                   .limit(page_size)\
                   .all()

    return parents


@router.get("/{parent_id}", response_model=ParentResponse)
async def get_parent(
    parent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific parent by ID.
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()

    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent with ID {parent_id} not found"
        )

    return parent


@router.put("/{parent_id}", response_model=ParentResponse)
async def update_parent(
    parent_id: UUID,
    parent_data: ParentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a parent's information.
    Only updates fields that are provided.
    """
    parent = db.query(Parent).filter(Parent.id == parent_id).first()

    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent with ID {parent_id} not found"
        )

    # Update only provided fields
    update_data = parent_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(parent, field, value)

    db.commit()
    db.refresh(parent)

    return parent


@router.delete("/{parent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_parent(
    parent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a parent profile.
    Note: This will also remove all child-parent relationships.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete parent profiles"
        )

    parent = db.query(Parent).filter(Parent.id == parent_id).first()

    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent with ID {parent_id} not found"
        )

    db.delete(parent)
    db.commit()

    return None


# ============================================
# CHILD-PARENT RELATIONSHIP ENDPOINTS
# ============================================

@router.post("/relationships/", response_model=ChildParentResponse, status_code=status.HTTP_201_CREATED)
async def create_child_parent_relationship(
    relationship_data: ChildParentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a relationship between a child and parent.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == relationship_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {relationship_data.child_id} not found"
        )

    # Verify parent exists
    parent = db.query(Parent).filter(Parent.id == relationship_data.parent_id).first()
    if not parent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Parent with ID {relationship_data.parent_id} not found"
        )

    # Check if relationship already exists
    existing = db.query(ChildParent).filter(
        ChildParent.child_id == relationship_data.child_id,
        ChildParent.parent_id == relationship_data.parent_id
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Relationship between this child and parent already exists"
        )

    new_relationship = ChildParent(**relationship_data.model_dump())

    db.add(new_relationship)
    db.commit()
    db.refresh(new_relationship)

    return new_relationship


@router.get("/relationships/child/{child_id}", response_model=List[ChildParentResponse])
async def get_child_parents(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all parents/guardians for a specific child.
    """
    relationships = db.query(ChildParent)\
        .filter(ChildParent.child_id == child_id)\
        .all()

    return relationships


@router.get("/relationships/parent/{parent_id}", response_model=List[ChildParentResponse])
async def get_parent_children(
    parent_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all children for a specific parent/guardian.
    """
    relationships = db.query(ChildParent)\
        .filter(ChildParent.parent_id == parent_id)\
        .all()

    return relationships


@router.put("/relationships/{relationship_id}", response_model=ChildParentResponse)
async def update_child_parent_relationship(
    relationship_id: UUID,
    relationship_data: ChildParentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a child-parent relationship.
    Can update relationship type, custody status, pickup authorization, etc.
    """
    relationship = db.query(ChildParent).filter(ChildParent.id == relationship_id).first()

    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found"
        )

    # Update only provided fields
    update_data = relationship_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(relationship, field, value)

    db.commit()
    db.refresh(relationship)

    return relationship


@router.delete("/relationships/{relationship_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child_parent_relationship(
    relationship_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a child-parent relationship.
    """
    relationship = db.query(ChildParent).filter(ChildParent.id == relationship_id).first()

    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with ID {relationship_id} not found"
        )

    db.delete(relationship)
    db.commit()

    return None
