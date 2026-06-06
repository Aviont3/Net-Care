from datetime import date
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.child import Child
from app.models.communication import DailyReport
from app.schemas.communication import DailyReportResponse, DailyReportGenerate
from app.services import ai_service

router = APIRouter()


@router.post("/generate", response_model=DailyReportResponse, status_code=status.HTTP_201_CREATED)
async def generate_daily_report(
    payload: DailyReportGenerate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate (or regenerate) the AI daily report for a child on a given date."""
    child = db.query(Child).filter(Child.id == payload.child_id).first()
    if not child:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Child not found")

    try:
        result = ai_service.generate_report(db, payload.child_id, payload.report_date)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # Upsert: regenerate if one already exists for this child+date
    report = db.query(DailyReport).filter(
        DailyReport.child_id == payload.child_id,
        DailyReport.report_date == payload.report_date,
    ).first()

    if report:
        report.ai_generated_summary = result["summary_text"]
        report.activities_summary = result["activities_summary"]
        report.overall_mood = result["overall_mood"]
        report.generated_by = current_user.id
    else:
        report = DailyReport(
            child_id=payload.child_id,
            report_date=payload.report_date,
            ai_generated_summary=result["summary_text"],
            activities_summary=result["activities_summary"],
            overall_mood=result["overall_mood"],
            generated_by=current_user.id,
        )
        db.add(report)

    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=List[DailyReportResponse])
async def get_reports(
    child_id: Optional[UUID] = Query(None),
    report_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List daily reports, optionally filtered by child and/or date."""
    q = db.query(DailyReport)
    if child_id:
        q = q.filter(DailyReport.child_id == child_id)
    if report_date:
        q = q.filter(DailyReport.report_date == report_date)
    return q.order_by(DailyReport.report_date.desc()).limit(100).all()


@router.get("/{report_id}", response_model=DailyReportResponse)
async def get_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    report = db.query(DailyReport).filter(DailyReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report
