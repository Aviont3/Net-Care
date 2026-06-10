# Unified Calendar Endpoints
# ============================================
# Provides month overview, day detail, and per-child calendar views
# for the daycare management dashboard.

import calendar as cal
from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Date, and_, case, cast, func
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.child import Child
from app.models.communication import DailyReport
from app.models.daily_operations import Activity, Attendance
from app.models.health_safety import IncidentReport, MedicationLog
from app.models.user import User

router = APIRouter()


# ============================================
# Response Schemas
# ============================================


class CalendarDayOverview(PydanticBaseModel):
    """Single day summary for the month calendar grid."""

    date: str
    attendance_count: int
    meal_count: int
    activity_count: int
    incident_count: int
    medication_count: int
    report_count: int
    status: str  # "normal" | "attention" | "incident"

    class Config:
        from_attributes = True


class MonthOverviewResponse(PydanticBaseModel):
    """Full month calendar response."""

    year: int
    month: int
    total_active_children: int
    days: List[CalendarDayOverview]


class AttendanceDetail(PydanticBaseModel):
    child_name: str
    check_in_time: str
    check_out_time: Optional[str] = None
    is_late_pickup: bool


class ActivityDetail(PydanticBaseModel):
    child_name: str
    activity_type: str
    activity_name: str
    time: str
    mood: Optional[str] = None
    duration_minutes: Optional[int] = None


class MealDetail(PydanticBaseModel):
    child_name: str
    activity_name: str
    time: str


class IncidentDetail(PydanticBaseModel):
    child_name: str
    incident_type: str
    description: str
    time: str
    parent_notified: bool


class MedicationDetail(PydanticBaseModel):
    child_name: str
    medication_name: str
    dosage_given: str
    time: str
    administered_by: str


class ReportDetail(PydanticBaseModel):
    child_name: str
    id: str
    generated_at: str


class DaySummary(PydanticBaseModel):
    total_attendance: int
    total_activities: int
    total_meals: int
    total_incidents: int
    total_medications: int
    total_reports: int


class DayDetailResponse(PydanticBaseModel):
    """Full day detail with all records."""

    date: str
    attendance: List[AttendanceDetail]
    activities: List[ActivityDetail]
    meals: List[MealDetail]
    incidents: List[IncidentDetail]
    medications: List[MedicationDetail]
    reports: List[ReportDetail]
    summary: DaySummary


# ============================================
# Endpoints
# ============================================


@router.get("/month", response_model=MonthOverviewResponse)
async def get_month_overview(
    year: int = Query(..., ge=2020, le=2100, description="Calendar year"),
    month: int = Query(..., ge=1, le=12, description="Calendar month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a month overview with aggregated daily counts.

    Returns one row per day in the month with attendance, meal, activity,
    incident, medication, and report counts plus a computed status field.

    Uses a single optimized SQL query with LEFT JOINs and GROUP BY for
    performance (target < 500ms).
    """
    # Determine date range for the month
    _, last_day = cal.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    # Get total active children for percentage-based status calculation
    total_active_children = (
        db.query(func.count(Child.id))
        .filter(Child.is_active == True)
        .scalar()
        or 0
    )

    # Build subqueries for each data source, grouped by date
    attendance_sub = (
        db.query(
            Attendance.attendance_date.label("day"),
            func.count(Attendance.id).label("attendance_count"),
        )
        .filter(
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
        )
        .group_by(Attendance.attendance_date)
        .subquery()
    )

    meals_sub = (
        db.query(
            Activity.activity_date.label("day"),
            func.count(Activity.id).label("meal_count"),
        )
        .filter(
            Activity.activity_date >= start_date,
            Activity.activity_date <= end_date,
            Activity.activity_type == "meal",
        )
        .group_by(Activity.activity_date)
        .subquery()
    )

    activities_sub = (
        db.query(
            Activity.activity_date.label("day"),
            func.count(Activity.id).label("activity_count"),
        )
        .filter(
            Activity.activity_date >= start_date,
            Activity.activity_date <= end_date,
        )
        .group_by(Activity.activity_date)
        .subquery()
    )

    incidents_sub = (
        db.query(
            IncidentReport.incident_date.label("day"),
            func.count(IncidentReport.id).label("incident_count"),
        )
        .filter(
            IncidentReport.incident_date >= start_date,
            IncidentReport.incident_date <= end_date,
        )
        .group_by(IncidentReport.incident_date)
        .subquery()
    )

    medications_sub = (
        db.query(
            MedicationLog.administration_date.label("day"),
            func.count(MedicationLog.id).label("medication_count"),
        )
        .filter(
            MedicationLog.administration_date >= start_date,
            MedicationLog.administration_date <= end_date,
        )
        .group_by(MedicationLog.administration_date)
        .subquery()
    )

    reports_sub = (
        db.query(
            DailyReport.report_date.label("day"),
            func.count(DailyReport.id).label("report_count"),
        )
        .filter(
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date,
        )
        .group_by(DailyReport.report_date)
        .subquery()
    )

    # Generate all dates in the month using generate_series (PostgreSQL)
    # Fallback: query all subqueries and merge in Python for portability
    # We use the subquery approach merged in Python for database-agnostic code.

    # Collect results from each subquery into dictionaries keyed by date
    attendance_map: dict[date, int] = {}
    for row in db.query(attendance_sub):
        attendance_map[row.day] = row.attendance_count

    meals_map: dict[date, int] = {}
    for row in db.query(meals_sub):
        meals_map[row.day] = row.meal_count

    activities_map: dict[date, int] = {}
    for row in db.query(activities_sub):
        activities_map[row.day] = row.activity_count

    incidents_map: dict[date, int] = {}
    for row in db.query(incidents_sub):
        incidents_map[row.day] = row.incident_count

    medications_map: dict[date, int] = {}
    for row in db.query(medications_sub):
        medications_map[row.day] = row.medication_count

    reports_map: dict[date, int] = {}
    for row in db.query(reports_sub):
        reports_map[row.day] = row.report_count

    # Build response for every day in the month
    days: List[CalendarDayOverview] = []
    for day_num in range(1, last_day + 1):
        current_date = date(year, month, day_num)
        att_count = attendance_map.get(current_date, 0)
        inc_count = incidents_map.get(current_date, 0)

        # Determine status
        if inc_count > 0:
            day_status = "incident"
        elif total_active_children > 0 and att_count < (total_active_children * 0.5):
            day_status = "attention"
        else:
            day_status = "normal"

        days.append(
            CalendarDayOverview(
                date=current_date.isoformat(),
                attendance_count=att_count,
                meal_count=meals_map.get(current_date, 0),
                activity_count=activities_map.get(current_date, 0),
                incident_count=inc_count,
                medication_count=medications_map.get(current_date, 0),
                report_count=reports_map.get(current_date, 0),
                status=day_status,
            )
        )

    return MonthOverviewResponse(
        year=year,
        month=month,
        total_active_children=total_active_children,
        days=days,
    )


@router.get("/day", response_model=DayDetailResponse)
async def get_day_detail(
    date_param: date = Query(..., alias="date", description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get full day detail with all attendance, activity, meal, incident,
    medication, and report records for a specific date.

    Returns individual records with child names and a summary object.
    """
    # Attendance records with child names
    attendance_rows = (
        db.query(
            Attendance,
            func.concat(Child.first_name, " ", Child.last_name).label("child_name"),
        )
        .join(Child, Child.id == Attendance.child_id)
        .filter(Attendance.attendance_date == date_param)
        .order_by(Attendance.check_in_time)
        .all()
    )

    attendance_list = [
        AttendanceDetail(
            child_name=row.child_name,
            check_in_time=row.Attendance.check_in_time.strftime("%H:%M") if row.Attendance.check_in_time else "",
            check_out_time=row.Attendance.check_out_time.strftime("%H:%M") if row.Attendance.check_out_time else None,
            is_late_pickup=row.Attendance.is_late_pickup,
        )
        for row in attendance_rows
    ]

    # Activities (all types)
    activity_rows = (
        db.query(
            Activity,
            func.concat(Child.first_name, " ", Child.last_name).label("child_name"),
        )
        .join(Child, Child.id == Activity.child_id)
        .filter(Activity.activity_date == date_param)
        .order_by(Activity.activity_time)
        .all()
    )

    activities_list = [
        ActivityDetail(
            child_name=row.child_name,
            activity_type=row.Activity.activity_type,
            activity_name=row.Activity.activity_name,
            time=row.Activity.activity_time.strftime("%H:%M") if row.Activity.activity_time else "",
            mood=row.Activity.mood,
            duration_minutes=row.Activity.duration_minutes,
        )
        for row in activity_rows
    ]

    # Meals (filtered from activities where type="meal")
    meals_list = [
        MealDetail(
            child_name=row.child_name,
            activity_name=row.Activity.activity_name,
            time=row.Activity.activity_time.strftime("%H:%M") if row.Activity.activity_time else "",
        )
        for row in activity_rows
        if row.Activity.activity_type == "meal"
    ]

    # Incidents
    incident_rows = (
        db.query(
            IncidentReport,
            func.concat(Child.first_name, " ", Child.last_name).label("child_name"),
        )
        .join(Child, Child.id == IncidentReport.child_id)
        .filter(IncidentReport.incident_date == date_param)
        .order_by(IncidentReport.incident_time)
        .all()
    )

    incidents_list = [
        IncidentDetail(
            child_name=row.child_name,
            incident_type=row.IncidentReport.incident_type,
            description=row.IncidentReport.description,
            time=row.IncidentReport.incident_time.strftime("%H:%M") if row.IncidentReport.incident_time else "",
            parent_notified=row.IncidentReport.parent_notified,
        )
        for row in incident_rows
    ]

    # Medications
    medication_rows = (
        db.query(
            MedicationLog,
            func.concat(Child.first_name, " ", Child.last_name).label("child_name"),
            func.concat(User.first_name, " ", User.last_name).label("admin_name"),
        )
        .join(Child, Child.id == MedicationLog.child_id)
        .join(User, User.id == MedicationLog.administered_by)
        .filter(MedicationLog.administration_date == date_param)
        .order_by(MedicationLog.administration_time)
        .all()
    )

    medications_list = [
        MedicationDetail(
            child_name=row.child_name,
            medication_name=row.MedicationLog.authorization.medication_name,
            dosage_given=row.MedicationLog.dosage_given,
            time=row.MedicationLog.administration_time.strftime("%H:%M") if row.MedicationLog.administration_time else "",
            administered_by=row.admin_name,
        )
        for row in medication_rows
    ]

    # Daily Reports
    report_rows = (
        db.query(
            DailyReport,
            func.concat(Child.first_name, " ", Child.last_name).label("child_name"),
        )
        .join(Child, Child.id == DailyReport.child_id)
        .filter(DailyReport.report_date == date_param)
        .order_by(DailyReport.created_at)
        .all()
    )

    reports_list = [
        ReportDetail(
            child_name=row.child_name,
            id=str(row.DailyReport.id),
            generated_at=row.DailyReport.created_at.isoformat() if row.DailyReport.created_at else "",
        )
        for row in report_rows
    ]

    # Build summary
    summary = DaySummary(
        total_attendance=len(attendance_list),
        total_activities=len(activities_list),
        total_meals=len(meals_list),
        total_incidents=len(incidents_list),
        total_medications=len(medications_list),
        total_reports=len(reports_list),
    )

    return DayDetailResponse(
        date=date_param.isoformat(),
        attendance=attendance_list,
        activities=activities_list,
        meals=meals_list,
        incidents=incidents_list,
        medications=medications_list,
        reports=reports_list,
        summary=summary,
    )


@router.get("/child/{child_id}/month", response_model=MonthOverviewResponse)
async def get_child_month_overview(
    child_id: UUID,
    year: int = Query(..., ge=2020, le=2100, description="Calendar year"),
    month: int = Query(..., ge=1, le=12, description="Calendar month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a month overview for a specific child with aggregated daily counts.

    Same structure as the facility-wide month overview but filtered to a
    single child's records.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found",
        )

    # Determine date range for the month
    _, last_day = cal.monthrange(year, month)
    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    # For a single child the "total active children" is 1
    total_active_children = 1

    # Build subqueries filtered to the specific child
    attendance_sub = (
        db.query(
            Attendance.attendance_date.label("day"),
            func.count(Attendance.id).label("attendance_count"),
        )
        .filter(
            Attendance.child_id == child_id,
            Attendance.attendance_date >= start_date,
            Attendance.attendance_date <= end_date,
        )
        .group_by(Attendance.attendance_date)
        .subquery()
    )

    meals_sub = (
        db.query(
            Activity.activity_date.label("day"),
            func.count(Activity.id).label("meal_count"),
        )
        .filter(
            Activity.child_id == child_id,
            Activity.activity_date >= start_date,
            Activity.activity_date <= end_date,
            Activity.activity_type == "meal",
        )
        .group_by(Activity.activity_date)
        .subquery()
    )

    activities_sub = (
        db.query(
            Activity.activity_date.label("day"),
            func.count(Activity.id).label("activity_count"),
        )
        .filter(
            Activity.child_id == child_id,
            Activity.activity_date >= start_date,
            Activity.activity_date <= end_date,
        )
        .group_by(Activity.activity_date)
        .subquery()
    )

    incidents_sub = (
        db.query(
            IncidentReport.incident_date.label("day"),
            func.count(IncidentReport.id).label("incident_count"),
        )
        .filter(
            IncidentReport.child_id == child_id,
            IncidentReport.incident_date >= start_date,
            IncidentReport.incident_date <= end_date,
        )
        .group_by(IncidentReport.incident_date)
        .subquery()
    )

    medications_sub = (
        db.query(
            MedicationLog.administration_date.label("day"),
            func.count(MedicationLog.id).label("medication_count"),
        )
        .filter(
            MedicationLog.child_id == child_id,
            MedicationLog.administration_date >= start_date,
            MedicationLog.administration_date <= end_date,
        )
        .group_by(MedicationLog.administration_date)
        .subquery()
    )

    reports_sub = (
        db.query(
            DailyReport.report_date.label("day"),
            func.count(DailyReport.id).label("report_count"),
        )
        .filter(
            DailyReport.child_id == child_id,
            DailyReport.report_date >= start_date,
            DailyReport.report_date <= end_date,
        )
        .group_by(DailyReport.report_date)
        .subquery()
    )

    # Collect results into dictionaries keyed by date
    attendance_map: dict[date, int] = {}
    for row in db.query(attendance_sub):
        attendance_map[row.day] = row.attendance_count

    meals_map: dict[date, int] = {}
    for row in db.query(meals_sub):
        meals_map[row.day] = row.meal_count

    activities_map: dict[date, int] = {}
    for row in db.query(activities_sub):
        activities_map[row.day] = row.activity_count

    incidents_map: dict[date, int] = {}
    for row in db.query(incidents_sub):
        incidents_map[row.day] = row.incident_count

    medications_map: dict[date, int] = {}
    for row in db.query(medications_sub):
        medications_map[row.day] = row.medication_count

    reports_map: dict[date, int] = {}
    for row in db.query(reports_sub):
        reports_map[row.day] = row.report_count

    # Build response for every day in the month
    days: List[CalendarDayOverview] = []
    for day_num in range(1, last_day + 1):
        current_date = date(year, month, day_num)
        att_count = attendance_map.get(current_date, 0)
        inc_count = incidents_map.get(current_date, 0)

        # Determine status: for a single child, attendance < 1 means absent
        if inc_count > 0:
            day_status = "incident"
        elif att_count < 1:
            day_status = "attention"
        else:
            day_status = "normal"

        days.append(
            CalendarDayOverview(
                date=current_date.isoformat(),
                attendance_count=att_count,
                meal_count=meals_map.get(current_date, 0),
                activity_count=activities_map.get(current_date, 0),
                incident_count=inc_count,
                medication_count=medications_map.get(current_date, 0),
                report_count=reports_map.get(current_date, 0),
                status=day_status,
            )
        )

    return MonthOverviewResponse(
        year=year,
        month=month,
        total_active_children=total_active_children,
        days=days,
    )
