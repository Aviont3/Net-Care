from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date, timedelta
from uuid import UUID

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.child import Child, Parent, ChildParent
from app.models.communication import DailyReport
from app.models.daily_operations import Attendance

router = APIRouter()


def _get_parent_children(db: Session, current_user: User):
    """Resolve current user → Parent record → linked Child rows."""
    if current_user.role != "parent":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Parent access only")
    parent = db.query(Parent).filter(Parent.email == current_user.email).first()
    if not parent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No parent profile found for this account")
    child_ids = [cp.child_id for cp in db.query(ChildParent).filter(ChildParent.parent_id == parent.id).all()]
    return db.query(Child).filter(Child.id.in_(child_ids), Child.is_active == True).all()


def _verify_child_access(db: Session, current_user: User, child_id: UUID) -> Child:
    """Raise 403 if the current parent user doesn't have access to this child."""
    children = _get_parent_children(db, current_user)
    child = next((c for c in children if c.id == child_id), None)
    if not child:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this child's records")
    return child


@router.get("/children")
async def get_my_children(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get children linked to the current parent account."""
    children = _get_parent_children(db, current_user)
    today = date.today()
    result = []
    for c in children:
        attendance = db.query(Attendance).filter(
            Attendance.child_id == c.id,
            Attendance.attendance_date == today,
        ).first()
        report = db.query(DailyReport).filter(
            DailyReport.child_id == c.id,
            DailyReport.report_date == today,
        ).first()
        result.append({
            "id": str(c.id),
            "first_name": c.first_name,
            "last_name": c.last_name,
            "date_of_birth": c.date_of_birth.isoformat(),
            "photo_url": c.photo_url,
            "today_mood": report.overall_mood if report else None,
            "today_checked_in": attendance is not None,
            "today_checked_out": attendance.check_out_time is not None if attendance else False,
        })
    return result


@router.get("/children/{child_id}/reports")
async def get_child_reports(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get last 14 days of daily reports for a child (parent-access only)."""
    _verify_child_access(db, current_user, child_id)
    since = date.today() - timedelta(days=14)
    reports = (
        db.query(DailyReport)
        .filter(DailyReport.child_id == child_id, DailyReport.report_date >= since)
        .order_by(DailyReport.report_date.desc())
        .all()
    )
    return [
        {
            "id": str(r.id),
            "report_date": r.report_date.isoformat(),
            "ai_generated_summary": r.ai_generated_summary,
            "overall_mood": r.overall_mood,
            "custom_notes": r.custom_notes,
            "activities_summary": r.activities_summary,
        }
        for r in reports
    ]


@router.get("/children/{child_id}/attendance")
async def get_child_attendance(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get last 7 days of attendance for a child (parent-access only)."""
    _verify_child_access(db, current_user, child_id)
    since = date.today() - timedelta(days=7)
    records = (
        db.query(Attendance)
        .filter(Attendance.child_id == child_id, Attendance.attendance_date >= since)
        .order_by(Attendance.attendance_date.desc())
        .all()
    )
    return [
        {
            "id": str(a.id),
            "attendance_date": a.attendance_date.isoformat(),
            "check_in_time": a.check_in_time.strftime("%H:%M") if a.check_in_time else None,
            "check_out_time": a.check_out_time.strftime("%H:%M") if a.check_out_time else None,
        }
        for a in records
    ]
