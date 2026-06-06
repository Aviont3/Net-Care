from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date
from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.daily_operations import Attendance

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
