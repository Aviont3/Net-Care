"""
Monthly CACFP Claim Calculation Service
=========================================
Calculates reimbursable meal counts and dollar amounts from actual
attendance + activity records for a given calendar month.

Uses the claiming percentage method:
  - Determine free/reduced/paid split from current active eligibility records
  - Apply those percentages to total compliant meal counts
  - Sum reimbursement across all meal types
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.daily_operations import Activity, Attendance
from app.models.cacfp import CACFPEligibility
from app.services.cacfp_rates import RATES, CASH_IN_LIEU


def calculate_monthly_claim(db: Session, year: int, month: int) -> dict:
    """
    Calculate the monthly CACFP claim from recorded activities.

    Only meals that are:
      - activity_type = "meal"
      - meal_type is set (breakfast/lunch/supper/snack)
      - cacfp_compliant = True

    are counted toward reimbursement.

    Args:
        db:    SQLAlchemy session.
        year:  Calendar year (e.g. 2026).
        month: Calendar month 1–12.

    Returns:
        Dict with all fields needed to populate a CACFPMonthlyClaim row,
        plus a breakdown list for display purposes.
    """
    # ── 1. Compliant meal counts by meal_type ──────────────────────────────
    meal_rows = (
        db.query(
            Activity.meal_type,
            func.count(Activity.id).label("count"),
        )
        .filter(
            Activity.activity_type == "meal",
            Activity.meal_type.isnot(None),
            Activity.cacfp_compliant == True,  # noqa: E712
            extract("year", Activity.activity_date) == year,
            extract("month", Activity.activity_date) == month,
        )
        .group_by(Activity.meal_type)
        .all()
    )
    meal_counts: dict = {row.meal_type: row.count for row in meal_rows}

    # ── 2. Enrollment by eligibility tier (current active records) ─────────
    tier_rows = (
        db.query(
            CACFPEligibility.eligibility_tier,
            func.count(CACFPEligibility.id).label("count"),
        )
        .filter(CACFPEligibility.is_active == True)  # noqa: E712
        .group_by(CACFPEligibility.eligibility_tier)
        .all()
    )
    tier_counts: dict = {row.eligibility_tier: row.count for row in tier_rows}
    free_count    = tier_counts.get("free",    0)
    reduced_count = tier_counts.get("reduced", 0)
    paid_count    = tier_counts.get("paid",    0)
    total_enrolled = free_count + reduced_count + paid_count

    # ── 3. Reimbursement calculation (claiming percentage method) ──────────
    total_reimbursement = 0.0
    breakdown = []

    if total_enrolled > 0:
        free_pct    = free_count    / total_enrolled
        reduced_pct = reduced_count / total_enrolled
        paid_pct    = paid_count    / total_enrolled

        for meal_type, count in meal_counts.items():
            rate_key = meal_type if meal_type in RATES else "lunch"

            free_meals    = round(count * free_pct)
            reduced_meals = round(count * reduced_pct)
            # Assign remainder to paid to avoid rounding drift
            paid_meals    = count - free_meals - reduced_meals

            meal_amount  = (free_meals    * RATES[rate_key]["free"])
            meal_amount += (reduced_meals * RATES[rate_key]["reduced"])
            meal_amount += (paid_meals    * RATES[rate_key]["paid"])

            # Cash-in-lieu supplement for lunch and supper
            ciu_amount = 0.0
            if meal_type in ("lunch", "supper"):
                ciu_amount = count * CASH_IN_LIEU

            subtotal = meal_amount + ciu_amount
            total_reimbursement += subtotal

            breakdown.append({
                "meal_type":     meal_type,
                "total_served":  count,
                "free_meals":    free_meals,
                "reduced_meals": reduced_meals,
                "paid_meals":    paid_meals,
                "meal_amount":   round(meal_amount, 2),
                "ciu_amount":    round(ciu_amount, 2),
                "subtotal":      round(subtotal, 2),
            })

    # ── 4. Operating days (distinct dates with at least one meal activity) ──
    operating_days = (
        db.query(func.count(func.distinct(Activity.activity_date)))
        .filter(
            Activity.activity_type == "meal",
            extract("year", Activity.activity_date) == year,
            extract("month", Activity.activity_date) == month,
        )
        .scalar()
        or 0
    )

    # ── 5. Total attendance records for the month ──────────────────────────
    total_attendance = (
        db.query(func.count(Attendance.id))
        .filter(
            extract("year", Attendance.attendance_date) == year,
            extract("month", Attendance.attendance_date) == month,
        )
        .scalar()
        or 0
    )

    return {
        "claim_month":      month,
        "claim_year":       year,
        "operating_days":   operating_days,
        "total_attendance": total_attendance,
        "breakfast_count":  meal_counts.get("breakfast", 0),
        "lunch_count":      meal_counts.get("lunch",     0),
        "supper_count":     meal_counts.get("supper",    0),
        "snack_count":      meal_counts.get("snack",     0),
        "free_enrolled":    free_count,
        "reduced_enrolled": reduced_count,
        "paid_enrolled":    paid_count,
        "total_reimbursement": round(total_reimbursement, 2),
        # Extra display field — not persisted, stripped before DB insert
        "_breakdown": breakdown,
    }


def reconciliation_check(db: Session, year: int, month: int) -> dict:
    """
    5-day reconciliation: verify meal counts do not exceed attendance for a
    sample of operating days in the month.

    CACFP requires sponsors to perform this check as part of monthly claim
    validation — a center cannot claim more meals than children present.

    Args:
        db:    SQLAlchemy session.
        year:  Claim year.
        month: Claim month (1-12).

    Returns:
        {
            "days_checked": int,
            "all_valid": bool,
            "results": [
                {
                    "date": "YYYY-MM-DD",
                    "meal_count": int,
                    "attendance_count": int,
                    "valid": bool,       # meal_count <= attendance_count
                },
                ...
            ],
        }
    """
    import random

    # All distinct operating days that have at least one meal activity
    day_rows = (
        db.query(func.distinct(Activity.activity_date))
        .filter(
            Activity.activity_type == "meal",
            extract("year",  Activity.activity_date) == year,
            extract("month", Activity.activity_date) == month,
        )
        .all()
    )
    days = [row[0] for row in day_rows]

    # Sample up to 5 days (or all if fewer than 5)
    sample_days = random.sample(days, min(5, len(days)))

    results = []
    for day in sorted(sample_days):
        meal_count = (
            db.query(func.count(Activity.id))
            .filter(
                Activity.activity_type == "meal",
                Activity.activity_date == day,
            )
            .scalar()
            or 0
        )

        attendance_count = (
            db.query(func.count(Attendance.id))
            .filter(Attendance.attendance_date == day)
            .scalar()
            or 0
        )

        results.append(
            {
                "date":             day.isoformat(),
                "meal_count":       meal_count,
                "attendance_count": attendance_count,
                "valid":            meal_count <= attendance_count,
            }
        )

    all_valid = all(r["valid"] for r in results)
    return {
        "days_checked": len(results),
        "all_valid":    all_valid,
        "results":      results,
    }
