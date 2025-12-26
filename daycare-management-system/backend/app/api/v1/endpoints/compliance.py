# DCFS Compliance Endpoints
# ============================================
# Enrollment Forms, Immunization Records, Staff Credentials

from datetime import date
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.compliance import EnrollmentForm, ImmunizationRecord, StaffCredential
from app.models.child import Child
from app.models.user import User
from app.schemas.compliance import (
    EnrollmentFormCreate,
    EnrollmentFormUpdate,
    EnrollmentFormResponse,
    ImmunizationRecordCreate,
    ImmunizationRecordUpdate,
    ImmunizationRecordResponse,
    StaffCredentialCreate,
    StaffCredentialUpdate,
    StaffCredentialResponse,
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================
# ENROLLMENT FORMS (DCFS Form 602)
# ============================================

@router.post("/enrollment-forms/", response_model=EnrollmentFormResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment_form(
    form_data: EnrollmentFormCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create DCFS Form 602 - Child Enrollment Record.
    One form per child, contains all enrollment information.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == form_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {form_data.child_id} not found"
        )

    # Check if enrollment form already exists for this child
    existing = db.query(EnrollmentForm)\
        .filter(EnrollmentForm.child_id == form_data.child_id)\
        .first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Enrollment form already exists for this child (ID: {existing.id})"
        )

    new_form = EnrollmentForm(
        **form_data.model_dump(),
        completed_by=current_user.id if form_data.is_complete else None
    )

    db.add(new_form)
    db.commit()
    db.refresh(new_form)

    return new_form


@router.get("/enrollment-forms/", response_model=List[EnrollmentFormResponse])
async def get_enrollment_forms(
    is_complete: Optional[bool] = Query(None, description="Filter by completion status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all enrollment forms with optional filtering.
    """
    query = db.query(EnrollmentForm)

    if is_complete is not None:
        query = query.filter(EnrollmentForm.is_complete == is_complete)

    offset = (page - 1) * page_size
    forms = query.order_by(EnrollmentForm.enrollment_date.desc())\
                 .offset(offset)\
                 .limit(page_size)\
                 .all()

    return forms


@router.get("/enrollment-forms/child/{child_id}", response_model=EnrollmentFormResponse)
async def get_child_enrollment_form(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get enrollment form for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    form = db.query(EnrollmentForm)\
        .filter(EnrollmentForm.child_id == child_id)\
        .first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No enrollment form found for child with ID {child_id}"
        )

    return form


@router.get("/enrollment-forms/{form_id}", response_model=EnrollmentFormResponse)
async def get_enrollment_form(
    form_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific enrollment form by ID.
    """
    form = db.query(EnrollmentForm).filter(EnrollmentForm.id == form_id).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment form with ID {form_id} not found"
        )

    return form


@router.put("/enrollment-forms/{form_id}", response_model=EnrollmentFormResponse)
async def update_enrollment_form(
    form_id: UUID,
    form_data: EnrollmentFormUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an enrollment form.
    """
    form = db.query(EnrollmentForm).filter(EnrollmentForm.id == form_id).first()

    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment form with ID {form_id} not found"
        )

    # Update only provided fields
    update_data = form_data.model_dump(exclude_unset=True)

    # If marking as complete, set completed_by
    if 'is_complete' in update_data and update_data['is_complete'] and not form.is_complete:
        form.completed_by = current_user.id

    for field, value in update_data.items():
        setattr(form, field, value)

    db.commit()
    db.refresh(form)

    return form


@router.get("/enrollment-forms/incomplete/list", response_model=List[dict])
async def get_incomplete_enrollment_forms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of children with incomplete enrollment forms.
    Used for DCFS compliance tracking.
    """
    forms = db.query(EnrollmentForm)\
        .filter(EnrollmentForm.is_complete == False)\
        .all()

    incomplete_list = []
    for form in forms:
        child = db.query(Child).filter(Child.id == form.child_id).first()
        if child:
            incomplete_list.append({
                "form_id": str(form.id),
                "child_id": str(child.id),
                "child_name": f"{child.first_name} {child.last_name}",
                "enrollment_date": form.enrollment_date.isoformat(),
                "has_parent_signature": form.parent_signature_url is not None,
                "has_staff_signature": form.staff_signature_url is not None
            })

    return incomplete_list


# ============================================
# IMMUNIZATION RECORDS
# ============================================

@router.post("/immunizations/", response_model=ImmunizationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_immunization_record(
    record_data: ImmunizationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add an immunization record for a child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == record_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {record_data.child_id} not found"
        )

    new_record = ImmunizationRecord(**record_data.model_dump())

    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record


@router.get("/immunizations/child/{child_id}", response_model=List[ImmunizationRecordResponse])
async def get_child_immunizations(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all immunization records for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    records = db.query(ImmunizationRecord)\
        .filter(ImmunizationRecord.child_id == child_id)\
        .order_by(ImmunizationRecord.administration_date.desc())\
        .all()

    return records


@router.get("/immunizations/{record_id}", response_model=ImmunizationRecordResponse)
async def get_immunization_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific immunization record by ID.
    """
    record = db.query(ImmunizationRecord).filter(ImmunizationRecord.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Immunization record with ID {record_id} not found"
        )

    return record


@router.put("/immunizations/{record_id}", response_model=ImmunizationRecordResponse)
async def update_immunization_record(
    record_id: UUID,
    record_data: ImmunizationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an immunization record.
    """
    record = db.query(ImmunizationRecord).filter(ImmunizationRecord.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Immunization record with ID {record_id} not found"
        )

    # Update only provided fields
    update_data = record_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)

    db.commit()
    db.refresh(record)

    return record


@router.delete("/immunizations/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_immunization_record(
    record_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an immunization record.
    Only admins can delete for compliance reasons.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete immunization records"
        )

    record = db.query(ImmunizationRecord).filter(ImmunizationRecord.id == record_id).first()

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Immunization record with ID {record_id} not found"
        )

    db.delete(record)
    db.commit()

    return None


@router.get("/immunizations/expiring/soon", response_model=List[dict])
async def get_expiring_immunizations(
    days: int = Query(30, ge=1, le=365, description="Number of days ahead to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get immunization records expiring soon.
    Used for compliance alerts and parent notifications.
    """
    from datetime import timedelta

    cutoff_date = date.today() + timedelta(days=days)

    records = db.query(ImmunizationRecord)\
        .filter(
            ImmunizationRecord.expiration_date.isnot(None),
            ImmunizationRecord.expiration_date <= cutoff_date,
            ImmunizationRecord.expiration_date >= date.today()
        )\
        .order_by(ImmunizationRecord.expiration_date)\
        .all()

    expiring_list = []
    for record in records:
        child = db.query(Child).filter(Child.id == record.child_id).first()
        if child:
            days_until_expiration = (record.expiration_date - date.today()).days
            expiring_list.append({
                "record_id": str(record.id),
                "child_id": str(child.id),
                "child_name": f"{child.first_name} {child.last_name}",
                "vaccine_name": record.vaccine_name,
                "expiration_date": record.expiration_date.isoformat(),
                "days_until_expiration": days_until_expiration,
                "is_verified": record.is_verified
            })

    return expiring_list


# ============================================
# STAFF CREDENTIALS
# ============================================

@router.post("/staff-credentials/", response_model=StaffCredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_staff_credential(
    credential_data: StaffCredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a credential for a staff member.
    Required credentials: CPR, First Aid, Background Check, TB Test, DCFS Training
    """
    # Verify user exists
    user = db.query(User).filter(User.id == credential_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {credential_data.user_id} not found"
        )

    # Validate credential type
    valid_types = ['CPR', 'First Aid', 'Background Check', 'TB Test', 'DCFS Training', 'Fingerprinting', 'Mandated Reporter']
    if credential_data.credential_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid credential type. Must be one of: {', '.join(valid_types)}"
        )

    # Check if credential is expired
    is_expired = False
    if credential_data.expiration_date and credential_data.expiration_date < date.today():
        is_expired = True

    new_credential = StaffCredential(
        **credential_data.model_dump(),
        is_expired=is_expired
    )

    db.add(new_credential)
    db.commit()
    db.refresh(new_credential)

    return new_credential


@router.get("/staff-credentials/user/{user_id}", response_model=List[StaffCredentialResponse])
async def get_user_credentials(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all credentials for a specific staff member.
    """
    # Verify user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )

    credentials = db.query(StaffCredential)\
        .filter(StaffCredential.user_id == user_id)\
        .order_by(StaffCredential.expiration_date.asc().nullslast())\
        .all()

    return credentials


@router.get("/staff-credentials/{credential_id}", response_model=StaffCredentialResponse)
async def get_staff_credential(
    credential_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific staff credential by ID.
    """
    credential = db.query(StaffCredential).filter(StaffCredential.id == credential_id).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff credential with ID {credential_id} not found"
        )

    return credential


@router.put("/staff-credentials/{credential_id}", response_model=StaffCredentialResponse)
async def update_staff_credential(
    credential_id: UUID,
    credential_data: StaffCredentialUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a staff credential.
    """
    credential = db.query(StaffCredential).filter(StaffCredential.id == credential_id).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff credential with ID {credential_id} not found"
        )

    # Update only provided fields
    update_data = credential_data.model_dump(exclude_unset=True)

    # Re-check expiration if expiration_date is updated
    if 'expiration_date' in update_data:
        if update_data['expiration_date'] and update_data['expiration_date'] < date.today():
            credential.is_expired = True
        else:
            credential.is_expired = False

    for field, value in update_data.items():
        setattr(credential, field, value)

    db.commit()
    db.refresh(credential)

    return credential


@router.delete("/staff-credentials/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_staff_credential(
    credential_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a staff credential.
    Only admins can delete.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete staff credentials"
        )

    credential = db.query(StaffCredential).filter(StaffCredential.id == credential_id).first()

    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Staff credential with ID {credential_id} not found"
        )

    db.delete(credential)
    db.commit()

    return None


@router.get("/staff-credentials/expiring/soon", response_model=List[dict])
async def get_expiring_credentials(
    days: int = Query(30, ge=1, le=365, description="Number of days ahead to check"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get staff credentials expiring soon.
    Critical for DCFS compliance - staff must maintain current credentials.
    """
    from datetime import timedelta

    cutoff_date = date.today() + timedelta(days=days)

    credentials = db.query(StaffCredential)\
        .filter(
            StaffCredential.expiration_date.isnot(None),
            StaffCredential.expiration_date <= cutoff_date,
            StaffCredential.expiration_date >= date.today()
        )\
        .order_by(StaffCredential.expiration_date)\
        .all()

    expiring_list = []
    for credential in credentials:
        user = db.query(User).filter(User.id == credential.user_id).first()
        if user:
            days_until_expiration = (credential.expiration_date - date.today()).days
            expiring_list.append({
                "credential_id": str(credential.id),
                "user_id": str(user.id),
                "user_name": f"{user.first_name} {user.last_name}",
                "credential_type": credential.credential_type,
                "expiration_date": credential.expiration_date.isoformat(),
                "days_until_expiration": days_until_expiration,
                "is_verified": credential.is_verified
            })

    return expiring_list


@router.get("/staff-credentials/expired/list", response_model=List[dict])
async def get_expired_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all expired staff credentials.
    CRITICAL for DCFS compliance - staff with expired credentials cannot work.
    """
    credentials = db.query(StaffCredential)\
        .filter(StaffCredential.is_expired == True)\
        .order_by(StaffCredential.expiration_date.desc())\
        .all()

    expired_list = []
    for credential in credentials:
        user = db.query(User).filter(User.id == credential.user_id).first()
        if user:
            days_expired = (date.today() - credential.expiration_date).days if credential.expiration_date else 0
            expired_list.append({
                "credential_id": str(credential.id),
                "user_id": str(user.id),
                "user_name": f"{user.first_name} {user.last_name}",
                "credential_type": credential.credential_type,
                "expiration_date": credential.expiration_date.isoformat() if credential.expiration_date else None,
                "days_expired": days_expired
            })

    return expired_list
