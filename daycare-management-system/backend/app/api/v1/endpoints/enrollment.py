from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import date

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.child import Child, Parent, ChildParent, EmergencyContact, AuthorizedPickup

router = APIRouter()


# ── Input schemas ──────────────────────────────────────────────

class GuardianInput(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone_primary: str
    phone_secondary: Optional[str] = None
    address_street: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_zip: Optional[str] = None
    employer: Optional[str] = None
    work_phone: Optional[str] = None
    is_primary_contact: bool = False


class GuardianRelationship(BaseModel):
    guardian_index: int
    relationship_type: str
    is_primary: bool = False
    has_custody: bool = True
    can_pickup: bool = True


class ChildInput(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: date
    gender: Optional[str] = None
    allergies: Optional[str] = None
    dietary_restrictions: Optional[str] = None
    medical_conditions: Optional[str] = None
    special_needs: Optional[str] = None
    enrollment_date: date
    guardian_relationships: List[GuardianRelationship] = []


class EmergencyContactInput(BaseModel):
    name: str
    relationship_type: str
    phone_primary: str
    phone_secondary: Optional[str] = None
    priority_order: int = 1
    notes: Optional[str] = None


class FamilyEnrollmentRequest(BaseModel):
    guardians: List[GuardianInput]
    children: List[ChildInput]
    emergency_contacts: List[EmergencyContactInput] = []


# ── Endpoint ───────────────────────────────────────────────────

@router.post("/family", status_code=status.HTTP_201_CREATED)
async def enroll_family(
    payload: FamilyEnrollmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Enroll a complete family in one atomic transaction.
    Creates guardians, children, ChildParent links, and emergency contacts.
    """
    if not payload.guardians:
        raise HTTPException(status_code=400, detail="At least one guardian is required")
    if not payload.children:
        raise HTTPException(status_code=400, detail="At least one child is required")

    try:
        # 1. Create guardian (Parent) records
        created_parents: List[Parent] = []
        for g in payload.guardians:
            parent = Parent(**g.model_dump())
            db.add(parent)
            db.flush()  # get .id without committing
            created_parents.append(parent)

        # 2. Create child records + relationships
        created_children: List[Child] = []
        for child_input in payload.children:
            child_data = child_input.model_dump(exclude={"guardian_relationships"})
            child = Child(**child_data, created_by=current_user.id)
            db.add(child)
            db.flush()
            created_children.append(child)

            # Link to guardians
            for rel in child_input.guardian_relationships:
                if rel.guardian_index >= len(created_parents):
                    raise HTTPException(status_code=400, detail=f"guardian_index {rel.guardian_index} out of range")
                link = ChildParent(
                    child_id=child.id,
                    parent_id=created_parents[rel.guardian_index].id,
                    relationship_type=rel.relationship_type,
                    is_primary=rel.is_primary,
                    has_custody=rel.has_custody,
                    can_pickup=rel.can_pickup,
                )
                db.add(link)

        # 3. Create emergency contacts (linked to all children)
        for ec_input in payload.emergency_contacts:
            for child in created_children:
                ec = EmergencyContact(
                    child_id=child.id,
                    **ec_input.model_dump(),
                )
                db.add(ec)

        db.commit()

        return {
            "message": "Family enrolled successfully",
            "guardians": [{"id": str(p.id), "name": f"{p.first_name} {p.last_name}"} for p in created_parents],
            "children": [{"id": str(c.id), "name": f"{c.first_name} {c.last_name}"} for c in created_children],
        }

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Enrollment failed: {str(e)}")
