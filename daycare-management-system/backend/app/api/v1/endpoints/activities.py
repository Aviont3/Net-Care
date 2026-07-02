# Activities Management Endpoints
# ============================================

import os
import uuid as uuid_lib
from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
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
from app.services.cacfp_validator import validate_meal
from app.services.cacfp_audit import log_audit
from app.schemas.cacfp import ActivityCorrectionRequest

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

    try:
        new_activity = Activity(
            **activity_data.model_dump(),
            logged_by=current_user.id
        )

        # Auto-validate CACFP compliance when meal_type + food_components are present
        if (
            new_activity.activity_type == "meal"
            and new_activity.meal_type
            and new_activity.food_components
        ):
            result = validate_meal(new_activity.meal_type, new_activity.food_components)
            new_activity.cacfp_compliant = result["compliant"]
            new_activity.compliance_notes = result["notes"] if not result["compliant"] else None

        db.add(new_activity)
        db.commit()
        db.refresh(new_activity)

        # Immutable audit entry for CACFP meal records
        if new_activity.activity_type == "meal":
            log_audit(
                db,
                action="create",
                entity_type="meal_activity",
                entity_id=new_activity.id,
                performed_by=current_user.id,
            )
            db.commit()

        return new_activity
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating activity: {str(e)}"
        )


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
    CACFP meal records that have been validated (cacfp_compliant is set) are
    immutable — use POST /{activity_id}/correct instead.
    Only the staff member who logged it or an admin can update.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found"
        )

    # CACFP immutability guard — validated meal records require the correction workflow
    if activity.activity_type == "meal" and activity.cacfp_compliant is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "CACFP meal records cannot be edited directly after validation. "
                "Use POST /activities/{id}/correct with a documented reason."
            ),
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
    CACFP meal records (any meal activity) cannot be deleted — USDA requires
    3-year retention. Only the staff member who logged it or an admin can
    delete non-meal activities.
    """
    activity = db.query(Activity).filter(Activity.id == activity_id).first()

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity with ID {activity_id} not found"
        )

    # Hard block on all meal activity deletions
    if activity.activity_type == "meal":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "CACFP meal records cannot be deleted. "
                "USDA regulations require 3-year retention. "
                "Use POST /activities/{id}/correct to document errors."
            ),
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


# ============================================
# CACFP MEAL CORRECTION (immutable audit trail)
# ============================================

# Fields permitted for correction on a validated CACFP meal record.
# Structural fields (child_id, activity_date, logged_by) are never correctable.
_CORRECTABLE_FIELDS = {
    "activity_name", "description", "meal_type", "mood",
    "duration_minutes", "notes", "food_components",
}


@router.post("/{activity_id}/correct", response_model=ActivityResponse)
async def correct_meal_activity(
    activity_id: UUID,
    correction: ActivityCorrectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Apply a documented correction to a CACFP meal activity record.

    - `reason` is required — it is stored verbatim in the immutable audit log.
    - Only whitelisted fields may be corrected; structural fields (child_id,
      activity_date, logged_by) are never editable.
    - Creates a CACFPAuditLog entry capturing old_value → new_value.
    - If food_components or meal_type is corrected the CACFP compliance is
      automatically re-evaluated.
    - Only admins or the original logger may submit corrections.
    """
    if not correction.reason or not correction.reason.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A reason is required for all CACFP record corrections.",
        )

    if correction.field not in _CORRECTABLE_FIELDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                f"Field '{correction.field}' cannot be corrected. "
                f"Correctable fields: {', '.join(sorted(_CORRECTABLE_FIELDS))}."
            ),
        )

    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Activity not found")

    if activity.activity_type != "meal":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="The /correct endpoint is only for meal activities.",
        )

    if activity.logged_by != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the original logger or an admin may correct this record.",
        )

    # Capture old value
    old_val = getattr(activity, correction.field, None)
    old_val_str = str(old_val) if old_val is not None else None

    # Coerce new_value to the correct Python type
    field = correction.field
    new_val: object
    if field == "duration_minutes":
        try:
            new_val = int(correction.new_value)
        except ValueError:
            raise HTTPException(status_code=422, detail="duration_minutes must be an integer.")
    elif field == "food_components":
        import json
        try:
            new_val = json.loads(correction.new_value)
        except json.JSONDecodeError:
            raise HTTPException(status_code=422, detail="food_components must be valid JSON.")
    else:
        new_val = correction.new_value

    # Apply the correction
    setattr(activity, field, new_val)

    # Re-run CACFP validator if compliance-relevant fields changed
    if field in ("meal_type", "food_components"):
        meal_type = activity.meal_type
        food_components = activity.food_components
        if meal_type and food_components:
            from app.services.cacfp_validator import validate_meal
            result = validate_meal(meal_type, food_components)
            activity.cacfp_compliant = result["compliant"]
            activity.compliance_notes = result["notes"] if not result["compliant"] else None

    # Stage the audit entry in the same transaction
    log_audit(
        db,
        action="correction",
        entity_type="meal_activity",
        entity_id=activity.id,
        performed_by=current_user.id,
        field_changed=field,
        old_value=old_val_str,
        new_value=correction.new_value,
        reason=correction.reason.strip(),
    )

    db.commit()
    db.refresh(activity)
    return activity

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "uploads", "activities")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/{activity_id}/photo", response_model=ActivityResponse)
async def upload_activity_photo(
    activity_id: UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a photo attachment for an activity log.
    Max 1 photo per activity. Uploading again replaces the previous photo.
    Accepts: jpg, jpeg, png, gif, webp, heic (max 10MB).
    """
    # Verify activity exists
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Validate file extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")

    # Save file
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid_lib.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    # Update activity with photo URL
    photo_url = f"/uploads/activities/{filename}"
    activity.photo_url = photo_url
    db.commit()
    db.refresh(activity)

    return activity
