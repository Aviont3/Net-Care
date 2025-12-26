# Medication Management Endpoints
# ============================================
# Medication Authorizations & Administration Logs

from datetime import date, time
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.health_safety import MedicationAuthorization, MedicationLog
from app.models.child import Child
from app.models.user import User
from app.schemas.health_safety import (
    MedicationAuthorizationCreate,
    MedicationAuthorizationUpdate,
    MedicationAuthorizationResponse,
    MedicationLogCreate,
    MedicationLogUpdate,
    MedicationLogResponse,
)
from app.core.security import get_current_user

router = APIRouter()


# ============================================
# MEDICATION AUTHORIZATIONS
# ============================================

@router.post("/authorizations/", response_model=MedicationAuthorizationResponse, status_code=status.HTTP_201_CREATED)
async def create_medication_authorization(
    auth_data: MedicationAuthorizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create parent authorization for medication administration.
    DCFS REQUIRED: Staff cannot administer medication without written parent authorization.

    Must include:
    - Medication name and dosage
    - Administration frequency and instructions
    - Start and end dates
    - Parent signature (digital signature URL)
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == auth_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {auth_data.child_id} not found"
        )

    new_authorization = MedicationAuthorization(**auth_data.model_dump())

    db.add(new_authorization)
    db.commit()
    db.refresh(new_authorization)

    return new_authorization


@router.get("/authorizations/", response_model=List[MedicationAuthorizationResponse])
async def get_medication_authorizations(
    child_id: Optional[UUID] = Query(None, description="Filter by child"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medication authorizations with filtering.
    """
    query = db.query(MedicationAuthorization)

    if child_id:
        query = query.filter(MedicationAuthorization.child_id == child_id)

    if is_active is not None:
        query = query.filter(MedicationAuthorization.is_active == is_active)

    offset = (page - 1) * page_size
    authorizations = query.order_by(MedicationAuthorization.start_date.desc())\
                         .offset(offset)\
                         .limit(page_size)\
                         .all()

    return authorizations


@router.get("/authorizations/child/{child_id}", response_model=List[MedicationAuthorizationResponse])
async def get_child_medication_authorizations(
    child_id: UUID,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medication authorizations for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.child_id == child_id)

    if is_active is not None:
        query = query.filter(MedicationAuthorization.is_active == is_active)

    authorizations = query.order_by(MedicationAuthorization.start_date.desc()).all()

    return authorizations


@router.get("/authorizations/active/today", response_model=List[MedicationAuthorizationResponse])
async def get_active_medications_today(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all active medication authorizations for today.
    Use this to display which children need medication today.
    """
    today = date.today()

    authorizations = db.query(MedicationAuthorization)\
        .filter(
            MedicationAuthorization.is_active == True,
            MedicationAuthorization.start_date <= today,
            or_(
                MedicationAuthorization.end_date.is_(None),
                MedicationAuthorization.end_date >= today
            )
        )\
        .order_by(MedicationAuthorization.child_id)\
        .all()

    return authorizations


@router.get("/authorizations/{authorization_id}", response_model=MedicationAuthorizationResponse)
async def get_medication_authorization(
    authorization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific medication authorization by ID.
    """
    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {authorization_id} not found"
        )

    return authorization


@router.put("/authorizations/{authorization_id}", response_model=MedicationAuthorizationResponse)
async def update_medication_authorization(
    authorization_id: UUID,
    auth_data: MedicationAuthorizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a medication authorization.
    """
    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {authorization_id} not found"
        )

    # Update only provided fields
    update_data = auth_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(authorization, field, value)

    db.commit()
    db.refresh(authorization)

    return authorization


@router.patch("/authorizations/{authorization_id}/deactivate", response_model=MedicationAuthorizationResponse)
async def deactivate_medication_authorization(
    authorization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Deactivate a medication authorization.
    Use this when medication is discontinued.
    """
    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {authorization_id} not found"
        )

    authorization.is_active = False
    db.commit()
    db.refresh(authorization)

    return authorization


@router.delete("/authorizations/{authorization_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication_authorization(
    authorization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a medication authorization.
    Only admins can delete for compliance tracking.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete medication authorizations"
        )

    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {authorization_id} not found"
        )

    db.delete(authorization)
    db.commit()

    return None


# ============================================
# MEDICATION LOGS (Administration Records)
# ============================================

@router.post("/logs/", response_model=MedicationLogResponse, status_code=status.HTTP_201_CREATED)
async def create_medication_log(
    log_data: MedicationLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log medication administration.
    CRITICAL: Must record every time medication is given to a child.

    Requires:
    - Valid authorization
    - Staff signature
    - Date, time, and dosage
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == log_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {log_data.child_id} not found"
        )

    # Verify authorization exists and is active
    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == log_data.authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {log_data.authorization_id} not found"
        )

    if not authorization.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot log medication: Authorization is inactive"
        )

    # Verify authorization matches the child
    if authorization.child_id != log_data.child_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization does not match the specified child"
        )

    # Check if medication date is within authorization period
    if log_data.administration_date < authorization.start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Administration date is before authorization start date ({authorization.start_date})"
        )

    if authorization.end_date and log_data.administration_date > authorization.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Administration date is after authorization end date ({authorization.end_date})"
        )

    new_log = MedicationLog(
        **log_data.model_dump(),
        administered_by=current_user.id
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)

    return new_log


@router.get("/logs/", response_model=List[MedicationLogResponse])
async def get_medication_logs(
    child_id: Optional[UUID] = Query(None, description="Filter by child"),
    authorization_id: Optional[UUID] = Query(None, description="Filter by authorization"),
    administration_date: Optional[date] = Query(None, description="Filter by date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medication administration logs with filtering.
    """
    query = db.query(MedicationLog)

    if child_id:
        query = query.filter(MedicationLog.child_id == child_id)

    if authorization_id:
        query = query.filter(MedicationLog.authorization_id == authorization_id)

    if administration_date:
        query = query.filter(MedicationLog.administration_date == administration_date)

    offset = (page - 1) * page_size
    logs = query.order_by(
            MedicationLog.administration_date.desc(),
            MedicationLog.administration_time.desc()
        )\
        .offset(offset)\
        .limit(page_size)\
        .all()

    return logs


@router.get("/logs/child/{child_id}", response_model=List[MedicationLogResponse])
async def get_child_medication_logs(
    child_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medication administration history for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(MedicationLog).filter(MedicationLog.child_id == child_id)

    if start_date:
        query = query.filter(MedicationLog.administration_date >= start_date)
    if end_date:
        query = query.filter(MedicationLog.administration_date <= end_date)

    logs = query.order_by(MedicationLog.administration_date.desc()).all()

    return logs


@router.get("/logs/today", response_model=List[MedicationLogResponse])
async def get_todays_medication_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all medications administered today.
    Use for daily tracking and compliance verification.
    """
    today = date.today()

    logs = db.query(MedicationLog)\
        .filter(MedicationLog.administration_date == today)\
        .order_by(MedicationLog.administration_time.desc())\
        .all()

    return logs


@router.get("/logs/authorization/{authorization_id}", response_model=List[MedicationLogResponse])
async def get_authorization_medication_logs(
    authorization_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all administration logs for a specific medication authorization.
    """
    # Verify authorization exists
    authorization = db.query(MedicationAuthorization)\
        .filter(MedicationAuthorization.id == authorization_id)\
        .first()

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication authorization with ID {authorization_id} not found"
        )

    logs = db.query(MedicationLog)\
        .filter(MedicationLog.authorization_id == authorization_id)\
        .order_by(MedicationLog.administration_date.desc())\
        .all()

    return logs


@router.get("/logs/{log_id}", response_model=MedicationLogResponse)
async def get_medication_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific medication log by ID.
    """
    log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication log with ID {log_id} not found"
        )

    return log


@router.put("/logs/{log_id}", response_model=MedicationLogResponse)
async def update_medication_log(
    log_id: UUID,
    log_data: MedicationLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a medication log.
    Typically used to add parent notification status or additional notes.
    """
    log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication log with ID {log_id} not found"
        )

    # Only allow updates by the person who administered or by admin
    if log.administered_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update logs you created"
        )

    # Update only provided fields
    update_data = log_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(log, field, value)

    db.commit()
    db.refresh(log)

    return log


@router.delete("/logs/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medication_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a medication log.
    HIGHLY RESTRICTED: Only admins for compliance and legal liability.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete medication logs"
        )

    log = db.query(MedicationLog).filter(MedicationLog.id == log_id).first()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medication log with ID {log_id} not found"
        )

    db.delete(log)
    db.commit()

    return None


@router.get("/schedule/child/{child_id}/date/{schedule_date}", response_model=dict)
async def get_child_medication_schedule(
    child_id: UUID,
    schedule_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get medication schedule for a child on a specific date.
    Shows what medications are due and what has been administered.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    # Get active authorizations for the date
    active_authorizations = db.query(MedicationAuthorization)\
        .filter(
            MedicationAuthorization.child_id == child_id,
            MedicationAuthorization.is_active == True,
            MedicationAuthorization.start_date <= schedule_date,
            or_(
                MedicationAuthorization.end_date.is_(None),
                MedicationAuthorization.end_date >= schedule_date
            )
        )\
        .all()

    # Get logs for the date
    logs_today = db.query(MedicationLog)\
        .filter(
            MedicationLog.child_id == child_id,
            MedicationLog.administration_date == schedule_date
        )\
        .all()

    schedule = {
        "child_id": str(child_id),
        "child_name": f"{child.first_name} {child.last_name}",
        "date": schedule_date.isoformat(),
        "medications": []
    }

    for auth in active_authorizations:
        # Check if administered today
        administered_logs = [log for log in logs_today if log.authorization_id == auth.id]

        schedule["medications"].append({
            "authorization_id": str(auth.id),
            "medication_name": auth.medication_name,
            "dosage": auth.dosage,
            "frequency": auth.frequency,
            "instructions": auth.administration_instructions,
            "administered": len(administered_logs) > 0,
            "administration_times": [
                {
                    "time": log.administration_time.isoformat(),
                    "dosage_given": log.dosage_given,
                    "administered_by": str(log.administered_by)
                }
                for log in administered_logs
            ]
        })

    return schedule
