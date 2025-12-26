# Attendance Management Endpoints
# ============================================

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.daily_operations import Attendance
from app.models.child import Child
from app.models.user import User
from app.schemas.daily_operations import (
    AttendanceCreate,
    AttendanceCheckOut,
    AttendanceResponse,
)
from app.core.security import get_current_user
from app.core.config import settings

router = APIRouter()


@router.post("/check-in", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
async def check_in_child(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check in a child for the day.
    Records who dropped off the child and the check-in time.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == attendance_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {attendance_data.child_id} not found"
        )

    # Check if child is active
    if not child.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check in inactive child"
        )

    # Check if already checked in today
    today = date.today()
    existing = db.query(Attendance).filter(
        and_(
            Attendance.child_id == attendance_data.child_id,
            Attendance.attendance_date == today
        )
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Child already checked in today at {existing.check_in_time}"
        )

    # Create attendance record
    new_attendance = Attendance(
        child_id=attendance_data.child_id,
        attendance_date=today,
        check_in_time=attendance_data.check_in_time,
        check_in_by_name=attendance_data.check_in_by_name,
        check_in_signature_url=attendance_data.check_in_signature_url,
        notes=attendance_data.notes,
        recorded_by=current_user.id
    )

    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)

    return new_attendance


@router.patch("/{attendance_id}/check-out", response_model=AttendanceResponse)
async def check_out_child(
    attendance_id: UUID,
    checkout_data: AttendanceCheckOut,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check out a child at the end of the day.
    Records who picked up the child and calculates late pickup if applicable.
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )

    # Check if already checked out
    if attendance.check_out_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Child already checked out at {attendance.check_out_time}"
        )

    # Update checkout information
    attendance.check_out_time = checkout_data.check_out_time
    attendance.check_out_by_name = checkout_data.check_out_by_name
    attendance.check_out_signature_url = checkout_data.check_out_signature_url

    # Append checkout notes to existing notes
    if checkout_data.notes:
        if attendance.notes:
            attendance.notes += f"\n[Checkout] {checkout_data.notes}"
        else:
            attendance.notes = checkout_data.notes

    # Calculate late pickup
    # Assuming standard pickup time is 6:00 PM (18:00)
    standard_pickup = time(18, 0)  # 6:00 PM

    if checkout_data.check_out_time > standard_pickup:
        # Calculate minutes late
        checkout_datetime = datetime.combine(date.today(), checkout_data.check_out_time)
        standard_datetime = datetime.combine(date.today(), standard_pickup)
        late_minutes = int((checkout_datetime - standard_datetime).total_seconds() / 60)

        # Apply grace period
        if late_minutes > settings.LATE_PICKUP_GRACE_MINUTES:
            attendance.is_late_pickup = True
            attendance.late_pickup_minutes = late_minutes - settings.LATE_PICKUP_GRACE_MINUTES

    db.commit()
    db.refresh(attendance)

    return attendance


@router.get("/", response_model=List[AttendanceResponse])
async def get_attendance_records(
    attendance_date: Optional[date] = Query(None, description="Filter by specific date"),
    child_id: Optional[UUID] = Query(None, description="Filter by child ID"),
    checked_out: Optional[bool] = Query(None, description="Filter by checkout status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance records with optional filtering.
    """
    query = db.query(Attendance)

    # Apply filters
    if attendance_date:
        query = query.filter(Attendance.attendance_date == attendance_date)

    if child_id:
        query = query.filter(Attendance.child_id == child_id)

    if checked_out is not None:
        if checked_out:
            query = query.filter(Attendance.check_out_time.isnot(None))
        else:
            query = query.filter(Attendance.check_out_time.is_(None))

    # Apply pagination
    offset = (page - 1) * page_size
    records = query.order_by(Attendance.attendance_date.desc(), Attendance.check_in_time.desc())\
                   .offset(offset)\
                   .limit(page_size)\
                   .all()

    return records


@router.get("/today", response_model=List[AttendanceResponse])
async def get_today_attendance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all attendance records for today.
    Useful for displaying current attendance on dashboard.
    """
    today = date.today()
    records = db.query(Attendance)\
        .filter(Attendance.attendance_date == today)\
        .order_by(Attendance.check_in_time)\
        .all()

    return records


@router.get("/today/checked-in", response_model=List[AttendanceResponse])
async def get_currently_checked_in(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all children currently checked in (not yet checked out today).
    """
    today = date.today()
    records = db.query(Attendance)\
        .filter(
            and_(
                Attendance.attendance_date == today,
                Attendance.check_out_time.is_(None)
            )
        )\
        .order_by(Attendance.check_in_time)\
        .all()

    return records


@router.get("/child/{child_id}", response_model=List[AttendanceResponse])
async def get_child_attendance_history(
    child_id: UUID,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get attendance history for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(Attendance).filter(Attendance.child_id == child_id)

    # Apply date filters
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)

    # Apply pagination
    offset = (page - 1) * page_size
    records = query.order_by(Attendance.attendance_date.desc())\
                   .offset(offset)\
                   .limit(page_size)\
                   .all()

    return records


@router.get("/{attendance_id}", response_model=AttendanceResponse)
async def get_attendance_record(
    attendance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific attendance record by ID.
    """
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )

    return attendance


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attendance_record(
    attendance_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an attendance record.
    Only admins can delete attendance records for compliance reasons.
    """
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete attendance records"
        )

    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()

    if not attendance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with ID {attendance_id} not found"
        )

    db.delete(attendance)
    db.commit()

    return None


@router.get("/late-pickups/", response_model=List[AttendanceResponse])
async def get_late_pickups(
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all late pickup incidents.
    Useful for billing and compliance tracking.
    """
    query = db.query(Attendance).filter(Attendance.is_late_pickup == True)

    # Apply date filters
    if start_date:
        query = query.filter(Attendance.attendance_date >= start_date)
    if end_date:
        query = query.filter(Attendance.attendance_date <= end_date)

    records = query.order_by(Attendance.attendance_date.desc()).all()

    return records
