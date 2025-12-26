# Incident Reports Management Endpoints
# ============================================
# DCFS Form 337 - Incident and Accident Reports

from datetime import date, time
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.health_safety import IncidentReport
from app.models.child import Child
from app.models.user import User
from app.schemas.health_safety import (
    IncidentReportCreate,
    IncidentReportUpdate,
    IncidentReportResponse,
)
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=IncidentReportResponse, status_code=status.HTTP_201_CREATED)
async def create_incident_report(
    report_data: IncidentReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create DCFS Form 337 - Incident/Accident Report.
    Required for any injury, illness, behavioral incident, or accident.

    DCFS requires immediate documentation and parent notification.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == report_data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {report_data.child_id} not found"
        )

    # Validate incident type
    valid_types = ['injury', 'illness', 'behavioral', 'accident', 'other']
    if report_data.incident_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid incident type. Must be one of: {', '.join(valid_types)}"
        )

    # Validate notification method if provided
    if report_data.parent_notification_method:
        valid_methods = ['phone', 'email', 'in-person', 'sms']
        if report_data.parent_notification_method not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid notification method. Must be one of: {', '.join(valid_methods)}"
            )

    new_report = IncidentReport(
        **report_data.model_dump(),
        reported_by=current_user.id
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


@router.get("/", response_model=List[IncidentReportResponse])
async def get_incident_reports(
    child_id: Optional[UUID] = Query(None, description="Filter by child"),
    incident_type: Optional[str] = Query(None, description="Filter by incident type"),
    start_date: Optional[date] = Query(None, description="Start date"),
    end_date: Optional[date] = Query(None, description="End date"),
    parent_notified: Optional[bool] = Query(None, description="Filter by parent notification status"),
    dcfs_notification_required: Optional[bool] = Query(None, description="Filter by DCFS notification requirement"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get incident reports with comprehensive filtering options.
    """
    query = db.query(IncidentReport)

    # Apply filters
    if child_id:
        query = query.filter(IncidentReport.child_id == child_id)

    if incident_type:
        query = query.filter(IncidentReport.incident_type == incident_type)

    if start_date:
        query = query.filter(IncidentReport.incident_date >= start_date)

    if end_date:
        query = query.filter(IncidentReport.incident_date <= end_date)

    if parent_notified is not None:
        query = query.filter(IncidentReport.parent_notified == parent_notified)

    if dcfs_notification_required is not None:
        query = query.filter(IncidentReport.dcfs_notification_required == dcfs_notification_required)

    # Apply pagination
    offset = (page - 1) * page_size
    reports = query.order_by(IncidentReport.incident_date.desc(), IncidentReport.incident_time.desc())\
                   .offset(offset)\
                   .limit(page_size)\
                   .all()

    return reports


@router.get("/child/{child_id}", response_model=List[IncidentReportResponse])
async def get_child_incident_reports(
    child_id: UUID,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all incident reports for a specific child.
    """
    # Verify child exists
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {child_id} not found"
        )

    query = db.query(IncidentReport).filter(IncidentReport.child_id == child_id)

    if start_date:
        query = query.filter(IncidentReport.incident_date >= start_date)
    if end_date:
        query = query.filter(IncidentReport.incident_date <= end_date)

    reports = query.order_by(IncidentReport.incident_date.desc()).all()

    return reports


@router.get("/{report_id}", response_model=IncidentReportResponse)
async def get_incident_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific incident report by ID.
    """
    report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report with ID {report_id} not found"
        )

    return report


@router.put("/{report_id}", response_model=IncidentReportResponse)
async def update_incident_report(
    report_id: UUID,
    report_data: IncidentReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update an incident report.
    Typically used to add parent notification details, signatures, or DCFS notification info.
    """
    report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report with ID {report_id} not found"
        )

    # Update only provided fields
    update_data = report_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    db.commit()
    db.refresh(report)

    return report


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an incident report.
    RESTRICTED: Only admins can delete for compliance and legal reasons.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete incident reports"
        )

    report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report with ID {report_id} not found"
        )

    db.delete(report)
    db.commit()

    return None


@router.get("/pending/parent-notification", response_model=List[dict])
async def get_pending_parent_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get incident reports where parents have not yet been notified.
    CRITICAL: DCFS requires immediate parent notification for all incidents.
    """
    reports = db.query(IncidentReport)\
        .filter(IncidentReport.parent_notified == False)\
        .order_by(IncidentReport.incident_date.desc(), IncidentReport.incident_time.desc())\
        .all()

    pending_list = []
    for report in reports:
        child = db.query(Child).filter(Child.id == report.child_id).first()
        if child:
            from datetime import datetime
            incident_datetime = datetime.combine(report.incident_date, report.incident_time)
            hours_since_incident = (datetime.now() - incident_datetime).total_seconds() / 3600

            pending_list.append({
                "report_id": str(report.id),
                "child_id": str(child.id),
                "child_name": f"{child.first_name} {child.last_name}",
                "incident_type": report.incident_type,
                "incident_date": report.incident_date.isoformat(),
                "incident_time": report.incident_time.isoformat(),
                "hours_since_incident": round(hours_since_incident, 1),
                "description": report.description[:100] + "..." if len(report.description) > 100 else report.description
            })

    return pending_list


@router.get("/requiring/dcfs-notification", response_model=List[dict])
async def get_reports_requiring_dcfs_notification(
    notified: Optional[bool] = Query(None, description="Filter by notification status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get incident reports that require DCFS notification.
    Serious incidents must be reported to DCFS within specified timeframes.
    """
    query = db.query(IncidentReport)\
        .filter(IncidentReport.dcfs_notification_required == True)

    if notified is not None:
        if notified:
            query = query.filter(IncidentReport.dcfs_notified_at.isnot(None))
        else:
            query = query.filter(IncidentReport.dcfs_notified_at.is_(None))

    reports = query.order_by(IncidentReport.incident_date.desc()).all()

    dcfs_list = []
    for report in reports:
        child = db.query(Child).filter(Child.id == report.child_id).first()
        if child:
            dcfs_list.append({
                "report_id": str(report.id),
                "child_id": str(child.id),
                "child_name": f"{child.first_name} {child.last_name}",
                "incident_type": report.incident_type,
                "incident_date": report.incident_date.isoformat(),
                "incident_time": report.incident_time.isoformat(),
                "dcfs_notified": report.dcfs_notified_at is not None,
                "dcfs_notified_at": report.dcfs_notified_at.isoformat() if report.dcfs_notified_at else None,
                "description": report.description[:100] + "..." if len(report.description) > 100 else report.description
            })

    return dcfs_list


@router.get("/statistics/summary", response_model=dict)
async def get_incident_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get incident report statistics for a date range.
    Useful for safety analysis and compliance reporting.
    """
    query = db.query(IncidentReport)

    if start_date:
        query = query.filter(IncidentReport.incident_date >= start_date)
    if end_date:
        query = query.filter(IncidentReport.incident_date <= end_date)

    all_reports = query.all()

    # Calculate statistics
    stats = {
        "total_incidents": len(all_reports),
        "by_type": {},
        "parent_notification": {
            "notified": 0,
            "pending": 0
        },
        "dcfs_notification": {
            "required": 0,
            "completed": 0,
            "pending": 0
        },
        "injuries": 0,
        "date_range": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        }
    }

    for report in all_reports:
        # Count by type
        if report.incident_type not in stats["by_type"]:
            stats["by_type"][report.incident_type] = 0
        stats["by_type"][report.incident_type] += 1

        # Parent notification
        if report.parent_notified:
            stats["parent_notification"]["notified"] += 1
        else:
            stats["parent_notification"]["pending"] += 1

        # DCFS notification
        if report.dcfs_notification_required:
            stats["dcfs_notification"]["required"] += 1
            if report.dcfs_notified_at:
                stats["dcfs_notification"]["completed"] += 1
            else:
                stats["dcfs_notification"]["pending"] += 1

        # Count injuries
        if report.incident_type == "injury":
            stats["injuries"] += 1

    return stats


@router.patch("/{report_id}/notify-parent", response_model=IncidentReportResponse)
async def mark_parent_notified(
    report_id: UUID,
    notification_method: str = Query(..., description="phone, email, in-person, or sms"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an incident report as parent notified.
    Records the notification method and timestamp.
    """
    report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report with ID {report_id} not found"
        )

    # Validate notification method
    valid_methods = ['phone', 'email', 'in-person', 'sms']
    if notification_method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid notification method. Must be one of: {', '.join(valid_methods)}"
        )

    from datetime import datetime
    report.parent_notified = True
    report.parent_notified_at = datetime.now()
    report.parent_notification_method = notification_method

    db.commit()
    db.refresh(report)

    return report


@router.patch("/{report_id}/notify-dcfs", response_model=IncidentReportResponse)
async def mark_dcfs_notified(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark an incident report as DCFS notified.
    Records the notification timestamp.
    """
    report = db.query(IncidentReport).filter(IncidentReport.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Incident report with ID {report_id} not found"
        )

    if not report.dcfs_notification_required:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This incident does not require DCFS notification"
        )

    from datetime import datetime
    report.dcfs_notified_at = datetime.now()

    db.commit()
    db.refresh(report)

    return report
