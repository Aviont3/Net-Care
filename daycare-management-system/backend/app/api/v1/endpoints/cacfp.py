# CACFP (Child and Adult Care Food Program) Endpoints
# ============================================

import csv
import io
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cacfp import CACFPEligibility, CACFPMonthlyClaim, CACFPAuditLog
from app.models.child import Child
from app.models.user import User
from app.schemas.cacfp import (
    CACFPEligibilityCreate,
    CACFPEligibilityResponse,
    CACFPEligibilityUpdate,
    CACFPClaimCalculation,
    CACFPClaimCreate,
    CACFPClaimResponse,
    MealBreakdownItem,
    CACFPAuditLogResponse,
    ReconciliationCheckResponse,
)
from app.core.security import get_current_user
from app.services.cacfp_claims import calculate_monthly_claim, reconciliation_check
from app.services.cacfp_audit import log_audit

router = APIRouter()

_VALID_TIERS = {"free", "reduced", "paid"}

# Site name used in WINS CSV export (can be moved to settings table later)
_SITE_NAME = "Netta's Family Daycare"


# ============================================
# ELIGIBILITY ENDPOINTS
# ============================================

@router.post("/", response_model=CACFPEligibilityResponse, status_code=status.HTTP_201_CREATED)
async def create_eligibility(
    data: CACFPEligibilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a CACFP eligibility record for a child.
    Automatically deactivates any existing active record for that child
    so only one active record exists at a time.
    """
    if data.eligibility_tier not in _VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"eligibility_tier must be one of: {', '.join(sorted(_VALID_TIERS))}",
        )

    if data.expiration_date <= data.determination_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="expiration_date must be after determination_date",
        )

    child = db.query(Child).filter(Child.id == data.child_id).first()
    if not child:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Child with ID {data.child_id} not found",
        )

    # Deactivate existing active records for this child
    db.query(CACFPEligibility).filter(
        CACFPEligibility.child_id == data.child_id,
        CACFPEligibility.is_active == True,  # noqa: E712
    ).update({"is_active": False})

    record = CACFPEligibility(**data.model_dump())
    db.add(record)
    db.flush()  # get record.id before audit log

    log_audit(
        db,
        action="create",
        entity_type="eligibility",
        entity_id=record.id,
        performed_by=current_user.id,
        new_value=data.eligibility_tier,
    )

    db.commit()
    db.refresh(record)
    return record


@router.get("/", response_model=List[CACFPEligibilityResponse])
async def list_eligibility(
    child_id: Optional[UUID] = Query(None, description="Filter by child ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CACFP eligibility records, optionally filtered."""
    query = db.query(CACFPEligibility)
    if child_id is not None:
        query = query.filter(CACFPEligibility.child_id == child_id)
    if is_active is not None:
        query = query.filter(CACFPEligibility.is_active == is_active)
    return query.order_by(CACFPEligibility.determination_date.desc()).all()


@router.get("/child/{child_id}", response_model=CACFPEligibilityResponse)
async def get_active_eligibility_for_child(
    child_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the active CACFP eligibility record for a specific child."""
    record = (
        db.query(CACFPEligibility)
        .filter(
            CACFPEligibility.child_id == child_id,
            CACFPEligibility.is_active == True,  # noqa: E712
        )
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active CACFP eligibility record found for child {child_id}",
        )
    return record


@router.put("/{eligibility_id}", response_model=CACFPEligibilityResponse)
async def update_eligibility(
    eligibility_id: UUID,
    data: CACFPEligibilityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a CACFP eligibility record (partial update). Changes are audit-logged."""
    record = db.query(CACFPEligibility).filter(CACFPEligibility.id == eligibility_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"CACFP eligibility record {eligibility_id} not found",
        )
    if data.eligibility_tier is not None and data.eligibility_tier not in _VALID_TIERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"eligibility_tier must be one of: {', '.join(sorted(_VALID_TIERS))}",
        )

    updates = data.model_dump(exclude_unset=True)
    for field, new_val in updates.items():
        old_val = getattr(record, field, None)
        setattr(record, field, new_val)
        log_audit(
            db,
            action="correction",
            entity_type="eligibility",
            entity_id=record.id,
            performed_by=current_user.id,
            field_changed=field,
            old_value=str(old_val) if old_val is not None else None,
            new_value=str(new_val),
        )

    db.commit()
    db.refresh(record)
    return record


# ============================================
# MONTHLY CLAIMS ENDPOINTS
# ============================================

@router.get("/claims/calculate", response_model=CACFPClaimCalculation)
async def calculate_claim_preview(
    year: int = Query(..., ge=2020, le=2099, description="Claim year"),
    month: int = Query(..., ge=1, le=12, description="Claim month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Calculate a CACFP claim for the given month/year without saving it.
    Use this to preview before committing a draft.
    """
    result = calculate_monthly_claim(db, year, month)
    breakdown = [MealBreakdownItem(**item) for item in result.pop("_breakdown", [])]
    return CACFPClaimCalculation(**result, breakdown=breakdown)


@router.post("/claims/", response_model=CACFPClaimResponse, status_code=status.HTTP_201_CREATED)
async def save_claim_draft(
    data: CACFPClaimCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Save a monthly claim as a draft.
    If a draft already exists for the same month/year, it is replaced.
    """
    if current_user.role not in ("admin", "staff"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")

    # Replace any existing draft for this period
    db.query(CACFPMonthlyClaim).filter(
        CACFPMonthlyClaim.claim_year == data.claim_year,
        CACFPMonthlyClaim.claim_month == data.claim_month,
        CACFPMonthlyClaim.status == "draft",
    ).delete()

    claim = CACFPMonthlyClaim(**data.model_dump())
    db.add(claim)
    db.flush()

    log_audit(
        db,
        action="create",
        entity_type="claim",
        entity_id=claim.id,
        performed_by=current_user.id,
        new_value=f"{data.claim_year}-{data.claim_month:02d}",
    )

    db.commit()
    db.refresh(claim)
    return claim


@router.get("/claims/", response_model=List[CACFPClaimResponse])
async def list_claims(
    year: Optional[int] = Query(None, description="Filter by year"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all monthly CACFP claims, newest first."""
    query = db.query(CACFPMonthlyClaim)
    if year is not None:
        query = query.filter(CACFPMonthlyClaim.claim_year == year)
    if status_filter is not None:
        query = query.filter(CACFPMonthlyClaim.status == status_filter)
    return (
        query.order_by(
            CACFPMonthlyClaim.claim_year.desc(),
            CACFPMonthlyClaim.claim_month.desc(),
        )
        .all()
    )


@router.get("/claims/{claim_id}", response_model=CACFPClaimResponse)
async def get_claim(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific monthly claim by ID."""
    claim = db.query(CACFPMonthlyClaim).filter(CACFPMonthlyClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Claim {claim_id} not found")
    return claim


@router.patch("/claims/{claim_id}/submit", response_model=CACFPClaimResponse)
async def submit_claim(
    claim_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a claim as submitted. Only admin users can submit claims."""
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can submit claims")

    claim = db.query(CACFPMonthlyClaim).filter(CACFPMonthlyClaim.id == claim_id).first()
    if not claim:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Claim {claim_id} not found")
    if claim.status == "submitted":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Claim is already submitted")
    if claim.status == "approved":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Approved claims cannot be re-submitted")

    claim.status = "submitted"
    claim.submitted_at = datetime.now(timezone.utc)
    claim.submitted_by = current_user.id

    log_audit(
        db,
        action="submit_claim",
        entity_type="claim",
        entity_id=claim.id,
        performed_by=current_user.id,
        new_value="submitted",
    )

    db.commit()
    db.refresh(claim)
    return claim


@router.get("/claims/export/csv")
async def export_claim_csv(
    year: int = Query(..., ge=2020, le=2099, description="Claim year"),
    month: int = Query(..., ge=1, le=12, description="Claim month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export a WINS-compatible CSV for the given month/year.
    If a saved claim exists it is used; otherwise a live calculation is run.
    """
    claim_row = (
        db.query(CACFPMonthlyClaim)
        .filter(
            CACFPMonthlyClaim.claim_year == year,
            CACFPMonthlyClaim.claim_month == month,
        )
        .order_by(CACFPMonthlyClaim.status.desc(), CACFPMonthlyClaim.created_at.desc())
        .first()
    )

    if claim_row:
        data = {
            "claim_month":         claim_row.claim_month,
            "claim_year":          claim_row.claim_year,
            "operating_days":      claim_row.operating_days,
            "total_attendance":    claim_row.total_attendance,
            "breakfast_count":     claim_row.breakfast_count,
            "lunch_count":         claim_row.lunch_count,
            "supper_count":        claim_row.supper_count,
            "snack_count":         claim_row.snack_count,
            "free_enrolled":       claim_row.free_enrolled,
            "reduced_enrolled":    claim_row.reduced_enrolled,
            "paid_enrolled":       claim_row.paid_enrolled,
            "total_reimbursement": float(claim_row.total_reimbursement or 0),
        }
    else:
        data = calculate_monthly_claim(db, year, month)
        data.pop("_breakdown", None)

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=[
            "Site Name", "Claim Month", "Claim Year", "Operating Days",
            "Total Attendance", "Breakfast Count", "Lunch Count", "Supper Count",
            "Snack Count", "Free Enrolled", "Reduced Enrolled", "Paid Enrolled",
            "Total Reimbursement",
        ],
    )
    writer.writeheader()
    writer.writerow({
        "Site Name":           _SITE_NAME,
        "Claim Month":         data["claim_month"],
        "Claim Year":          data["claim_year"],
        "Operating Days":      data["operating_days"],
        "Total Attendance":    data["total_attendance"],
        "Breakfast Count":     data["breakfast_count"],
        "Lunch Count":         data["lunch_count"],
        "Supper Count":        data["supper_count"],
        "Snack Count":         data["snack_count"],
        "Free Enrolled":       data["free_enrolled"],
        "Reduced Enrolled":    data["reduced_enrolled"],
        "Paid Enrolled":       data["paid_enrolled"],
        "Total Reimbursement": f"{data['total_reimbursement']:.2f}",
    })

    filename = f"CACFP_Claim_{year}_{month:02d}.csv"
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/claims/reconciliation", response_model=ReconciliationCheckResponse)
async def run_reconciliation(
    year: int = Query(..., ge=2020, le=2099, description="Claim year"),
    month: int = Query(..., ge=1, le=12, description="Claim month (1-12)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run the 5-day reconciliation check for a claim period.
    Verifies that meal counts do not exceed attendance on sampled days.
    CACFP requires this as part of monthly claim validation.
    """
    result = reconciliation_check(db, year, month)
    return result


# ============================================
# AUDIT LOG ENDPOINTS
# ============================================

@router.get("/audit-log/", response_model=List[CACFPAuditLogResponse])
async def list_audit_log(
    entity_type: Optional[str] = Query(None, description="Filter by entity type (meal_activity, eligibility, claim)"),
    entity_id: Optional[UUID] = Query(None, description="Filter by entity ID"),
    performed_by: Optional[UUID] = Query(None, description="Filter by user who performed the action"),
    start_date: Optional[str] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date filter (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List CACFP audit log entries. Admin only.
    Supports filtering by entity_type, entity_id, performer, and date range.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    query = db.query(CACFPAuditLog)

    if entity_type:
        query = query.filter(CACFPAuditLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(CACFPAuditLog.entity_id == entity_id)
    if performed_by:
        query = query.filter(CACFPAuditLog.performed_by == performed_by)
    if start_date:
        query = query.filter(CACFPAuditLog.created_at >= start_date)
    if end_date:
        query = query.filter(CACFPAuditLog.created_at <= end_date)

    offset = (page - 1) * page_size
    return (
        query.order_by(CACFPAuditLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )


@router.get("/audit-log/entity/{entity_id}", response_model=List[CACFPAuditLogResponse])
async def get_entity_audit_trail(
    entity_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get the complete audit trail for a specific record (by entity_id).
    Returns all events in chronological order — useful for auditor review.
    Admin only.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    entries = (
        db.query(CACFPAuditLog)
        .filter(CACFPAuditLog.entity_id == entity_id)
        .order_by(CACFPAuditLog.created_at.asc())
        .all()
    )
    return entries
