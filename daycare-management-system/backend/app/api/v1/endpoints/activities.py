# Activities Management Endpoints
# ============================================

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models.daily_operations import Activity
from app.models.child import Child
from app.models.user import User
from app.schemas.daily_operations import (
    ActivityCreate,
    ActivityUpdate,
    ActivityResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log a new activity for a child.
    Activities include: meals, naps, diaper changes, play, learning, outdoor time.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == activity_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {activity_data.child_id} not found"
        )

    # Validate activity type
    valid_types = ['meal', 'nap', 'diaper', 'play', 'learning', 'outdoor']
    if activity_data.activity_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid activity type. Must be one of: {', '.join(valid_types)}"
        )

    # Validate mood if provided
    if activity_data.mood:
        valid_moods = ['happy', 'sad', 'energetic', 'tired', 'cranky', 'neutral']
        if activity_data.mood not in valid_moods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid mood. Must be one of: {', '.join(valid_moods)}"
            )

    new_activity = Activity(
        **activity_data.model_dump(),
        logged_by=current_user.id
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)

    return new_activity


@router.get("/", response_model=List[ActivityResponse])
async def get_activities(
    activity_date: Optional[date] = Query(None, description="Filter by specific date"),
    child_id: Optional[UUID] = Query(None, description="Filter by child ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(50, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity records with optional filtering.
    """
    query = db.query(Activity)

    # Apply filters
    if activity_date:
        query = query.filter(Activity.activity_date == activity_date)

    if child_id:
        query = query.filter(Activity.child_id == child_id)

    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)

    # Apply pagination
    offset = (page - 1) * page_size
    activities = query.order_by(Activity.activity_date.desc(), Activity.activity_time.desc())\
                     .offset(offset)\
                     .limit(page_size)\
                     .all()

    return activities


@router.get("/today", response_model=List[ActivityResponse])
async def get_today_activities(
    child_id: Optional[UUID] = Query(None, description="Filter by child ID"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all activities logged today.
    Useful for real-time daily report generation.
    """
    today = date.today()
    query = db.query(Activity).filter(Activity.activity_date == today)

    if child_id:
        query = query.filter(Activity.child_id == child_id)

    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)

    activities = query.order_by(Activity.activity_time.desc()).all()

    return activities


@router.get("/child/{child_id}", response_model=List[ActivityResponse])
async def get_child_activities(
    child_id: UUID,
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get activity history for a specific child.
    Useful for analyzing patterns and generating reports.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(Activity).filter(Activity.child_id == child_id)

    # Apply filters
    if start_date:
        query = query.filter(Activity.activity_date >= start_date)
    if end_date:
        query = query.filter(Activity.activity_date <= end_date)
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)

    # Apply pagination
    offset = (page - 1) * page_size
    activities = query.order_by(Activity.activity_date.desc(), Activity.activity_time.desc())\
                     .offset(offset)\
                     .limit(page_size)\
                     .all()

    return activities


@router.get("/child/{child_id}/date/{activity_date}", response_model=List[ActivityResponse])
async def get_child_activities_by_date(
    child_id: UUID,
    activity_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all activities for a specific child on a specific date.
    Used for generating daily reports.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    activities = db.query(Activity)\
        .filter(
            and_(
                Activity.child_id == child_id,
                Activity.activity_date == activity_date
            )
        )\
        .order_by(Activity.activity_time)\
        .all()

    return activities


@router.get("/summary/child/{child_id}/date/{activity_date}")
async def get_child_daily_activity_summary(
    child_id: UUID,
    activity_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a summary of activities for a child on a specific date.
    Returns counts by activity type and overall statistics.
    Useful for AI report generation.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    # Get all activities for the day
    activities = db.query(Activity)\
        .filter(
            and_(
                Activity.child_id == child_id,
                Activity.activity_date == activity_date
            )
        )\
        .all()

    # Calculate summary statistics
    summary = {
        "child_id": str(child_id),
        "child_name": f"{child.first_name} {child.last_name}",
        "date": activity_date.isoformat(),
        "total_activities": len(activities),
        "activities_by_type": {},
        "moods": [],
        "total_nap_duration": 0,
        "meal_count": 0,
        "diaper_count": 0,
    }

    # Process activities
    for activity in activities:
        # Count by type
        activity_type = activity.activity_type
        if activity_type not in summary["activities_by_type"]:
            summary["activities_by_type"][activity_type] = 0
        summary["activities_by_type"][activity_type] += 1

        # Track moods
        if activity.mood:
            summary["moods"].append(activity.mood)

        # Track specific metrics
        if activity_type == "nap" and activity.duration_minutes:
            summary["total_nap_duration"] += activity.duration_minutes
        elif activity_type == "meal":
            summary["meal_count"] += 1
        elif activity_type == "diaper":
            summary["diaper_count"] += 1

    # Calculate most common mood
    if summary["moods"]:
        from collections import Counter
        mood_counts = Counter(summary["moods"])
        summary["predominant_mood"] = mood_counts.most_common(1)[0][0]
    else:
        summary["predominant_mood"] = None

    return summary


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific activity by ID.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found"
        )

    return activity


@router.put("/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    activity_data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an activity record.
    Only the staff member who logged it or an admin can update.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found"
        )

    # Check permissions
    if activity.logged_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update activities you logged"
        )

    # Update only provided fields
    update_data = activity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(activity, field, value)

    db.commit()
    db.refresh(activity)

    return activity


@router.delete("/{activity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_activity(
    activity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an activity record.
    Only the staff member who logged it or an admin can delete.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found"
        )

    # Check permissions
    if activity.logged_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete activities you logged"
        )

    db.delete(activity)
    db.commit()

    return None
