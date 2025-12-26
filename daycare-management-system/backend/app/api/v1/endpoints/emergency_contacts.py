# Emergency Contacts Management Endpoints
# ============================================

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.child import EmergencyContact, Child
from app.models.user import User
from app.schemas.child import (
    EmergencyContactCreate,
    EmergencyContactUpdate,
    EmergencyContactResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def create_emergency_contact(
    contact_data: EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new emergency contact for a child.
    DCFS requires minimum 2 emergency contacts per child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == contact_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {contact_data.child_id} not found"
        )

    # Check if priority order is already taken for this child
    existing = db.query(EmergencyContact).filter(
        and_(
            EmergencyContact.child_id == contact_data.child_id,
            EmergencyContact.priority_order == contact_data.priority_order
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Priority order {contact_data.priority_order} is already assigned to another contact for this child"
        )

    new_contact = EmergencyContact(**contact_data.model_dump())

    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)

    return new_contact


@router.get("/child/{child_id}", response_model=List[EmergencyContactResponse])
async def get_child_emergency_contacts(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all emergency contacts for a specific child, ordered by priority.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    contacts = db.query(EmergencyContact)\
        .filter(EmergencyContact.child_id == child_id)\
        .order_by(EmergencyContact.priority_order)\
        .all()

    # DCFS Compliance Check: Warn if less than 2 contacts
    if len(contacts) < 2:
        # Note: In production, you might want to create a compliance alert here
        pass

    return contacts


@router.get("/{contact_id}", response_model=EmergencyContactResponse)
async def get_emergency_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific emergency contact by ID.
    """
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency contact with ID {contact_id} not found"
        )

    return contact


@router.put("/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: UUID,
    contact_data: EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an emergency contact's information.
    """
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency contact with ID {contact_id} not found"
        )

    # If updating priority order, check for conflicts
    update_data = contact_data.model_dump(exclude_unset=True)
    if 'priority_order' in update_data and update_data['priority_order'] != contact.priority_order:
        existing = db.query(EmergencyContact).filter(
            and_(
                EmergencyContact.child_id == contact.child_id,
                EmergencyContact.priority_order == update_data['priority_order'],
                EmergencyContact.id != contact_id
            )
        ).first()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Priority order {update_data['priority_order']} is already assigned to another contact"
            )

    # Update only provided fields
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)

    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an emergency contact.
    Warning: DCFS requires minimum 2 emergency contacts per child.
    """
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency contact with ID {contact_id} not found"
        )

    # Check DCFS compliance: Don't allow deletion if only 2 contacts exist
    remaining_contacts = db.query(EmergencyContact)\
        .filter(EmergencyContact.child_id == contact.child_id)\
        .count()

    if remaining_contacts <= 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete emergency contact. DCFS requires minimum 2 emergency contacts per child."
        )

    db.delete(contact)
    db.commit()

    return None


@router.patch("/{contact_id}/reorder/{new_priority}", response_model=EmergencyContactResponse)
async def reorder_emergency_contact(
    contact_id: UUID,
    new_priority: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Change the priority order of an emergency contact.
    Automatically adjusts other contacts' priorities to avoid conflicts.
    """
    contact = db.query(EmergencyContact).filter(EmergencyContact.id == contact_id).first()

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Emergency contact with ID {contact_id} not found"
        )

    old_priority = contact.priority_order

    if old_priority == new_priority:
        return contact

    # Get all contacts for this child
    all_contacts = db.query(EmergencyContact)\
        .filter(EmergencyContact.child_id == contact.child_id)\
        .order_by(EmergencyContact.priority_order)\
        .all()

    # Reorder priorities
    if new_priority < old_priority:
        # Moving up: shift others down
        for c in all_contacts:
            if c.id != contact_id and new_priority <= c.priority_order < old_priority:
                c.priority_order += 1
    else:
        # Moving down: shift others up
        for c in all_contacts:
            if c.id != contact_id and old_priority < c.priority_order <= new_priority:
                c.priority_order -= 1

    # Set new priority
    contact.priority_order = new_priority

    db.commit()
    db.refresh(contact)

    return contact


@router.get("/compliance/missing", response_model=List[dict])
async def get_children_missing_emergency_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of children who don't have the required minimum 2 emergency contacts.
    Used for DCFS compliance reporting.
    """
    # Get all active children
    children = db.query(Child).filter(Child.is_active == True).all()

    missing_contacts = []

    for child in children:
        contact_count = db.query(EmergencyContact)\
            .filter(EmergencyContact.child_id == child.id)\
            .count()

        if contact_count < 2:
            missing_contacts.append({
                "child_id": str(child.id),
                "child_name": f"{child.first_name} {child.last_name}",
                "current_contact_count": contact_count,
                "required_count": 2,
                "missing_count": 2 - contact_count
            })

    return missing_contacts
