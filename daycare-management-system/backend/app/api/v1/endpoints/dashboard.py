from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, Date
from datetime import date
from typing import Optional

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.daily_operations import Attendance, Activity
from app.models.health_safety import IncidentReport

router = APIRouter()


@router.get("/summary")
async def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dashboard summary statistics."""
    today = date.today()

    total_children = db.query(func.count(Child.id)).filter(Child.is_active == True).scalar() or 0

    present_today = db.query(func.count(Attendance.id)).filter(
        Attendance.attendance_date == today,
        Attendance.check_out_time == None
    ).scalar() or 0

    staff_count = db.query(func.count(User.id)).filter(
        User.is_active == True,
        User.role.in_(["staff", "admin"])
    ).scalar() or 0

    pending_alerts = 0

    attendance_pct = round((present_today / total_children * 100), 1) if total_children > 0 else 0

    return {
        "total_children": total_children,
        "present_today": present_today,
        "staff_on_duty": staff_count,
        "pending_alerts": pending_alerts,
        "attendance_percentage": attendance_pct,
    }


@router.get("/calendar-summary")
async def get_calendar_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return per-day activity counts for a date range.
    Used by the dashboard mini-calendar.
    """
    # Attendance counts per day
    attendance_rows = (
        db.query(Attendance.attendance_date, func.count(Attendance.id).label("cnt"))
        .filter(Attendance.attendance_date >= start_date, Attendance.attendance_date <= end_date)
        .group_by(Attendance.attendance_date)
        .all()
    )

    # Activity counts per day (all types)
    activity_rows = (
        db.query(Activity.activity_date, func.count(Activity.id).label("cnt"))
        .filter(Activity.activity_date >= start_date, Activity.activity_date <= end_date)
        .group_by(Activity.activity_date)
        .all()
    )

    # Meal counts per day
    meal_rows = (
        db.query(Activity.activity_date, func.count(Activity.id).label("cnt"))
        .filter(
            Activity.activity_date >= start_date,
            Activity.activity_date <= end_date,
            Activity.activity_type == "meal",
        )
        .group_by(Activity.activity_date)
        .all()
    )

    # Incident counts per day
    incident_rows = (
        db.query(IncidentReport.incident_date, func.count(IncidentReport.id).label("cnt"))
        .filter(IncidentReport.incident_date >= start_date, IncidentReport.incident_date <= end_date)
        .group_by(IncidentReport.incident_date)
        .all()
    )

    # Merge into a dict keyed by date string
    data: dict = {}

    def add(rows, field):
        for row in rows:
            key = row[0].isoformat()
            if key not in data:
                data[key] = {"date": key, "attendance_count": 0, "activity_count": 0, "meal_count": 0, "incident_count": 0}
            data[key][field] += row[1]

    add(attendance_rows, "attendance_count")
    add(activity_rows, "activity_count")
    add(meal_rows, "meal_count")
    add(incident_rows, "incident_count")

    return list(data.values())
