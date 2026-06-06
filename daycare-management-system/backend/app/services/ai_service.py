"""AI Service — generates daily reports for parents.
Phase 1: Template-based (no external API calls).
Phase 2: GPT-4 narratives (future, requires PII redaction)."""

from collections import Counter
from datetime import date
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.daily_operations import Activity, Attendance
from app.models.child import Child


def generate_report(db: Session, child_id: UUID, report_date: date, use_llm: bool = False) -> dict:
    """Generate a daily report. Returns summary_text, activities_summary, overall_mood."""
    if use_llm:
        raise NotImplementedError("LLM report generation is not yet enabled (Phase 2).")
    return _generate_template_report(db, child_id, report_date)


def _generate_template_report(db: Session, child_id: UUID, report_date: date) -> dict:
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child {child_id} not found")

    name = child.first_name
    activities = db.query(Activity).filter(
        Activity.child_id == child_id,
        Activity.activity_date == report_date
    ).order_by(Activity.activity_time).all()

    attendance = db.query(Attendance).filter(
        Attendance.child_id == child_id,
        Attendance.attendance_date == report_date
    ).first()

    # --- Build structured summary ---
    by_type: dict = {}
    moods = []
    total_nap_min = 0

    for a in activities:
        by_type.setdefault(a.activity_type, []).append(a.activity_name)
        if a.mood:
            moods.append(a.mood)
        if a.activity_type == "nap" and a.duration_minutes:
            total_nap_min += a.duration_minutes

    overall_mood = Counter(moods).most_common(1)[0][0] if moods else None

    activities_summary = {
        "by_type": {t: {"count": len(names), "items": names} for t, names in by_type.items()},
        "total_activities": len(activities),
        "total_nap_minutes": total_nap_min,
        "meal_count": len(by_type.get("meal", [])),
        "diaper_count": len(by_type.get("diaper", [])),
    }

    # --- Build narrative text ---
    day_str = report_date.strftime("%A, %B %-d")
    lines = [f"Hi! Here's a recap of {name}'s day on {day_str}. 🌟"]

    if attendance:
        check_in = attendance.check_in_time.strftime("%-I:%M %p") if attendance.check_in_time else None
        check_out = attendance.check_out_time.strftime("%-I:%M %p") if attendance.check_out_time else None
        if check_in and check_out:
            lines.append(f"{name} arrived at {check_in} and was picked up at {check_out}.")
        elif check_in:
            lines.append(f"{name} arrived at {check_in}.")

    if not activities:
        lines.append("No activities were logged today.")
    else:
        if "meal" in by_type:
            meals = by_type["meal"]
            lines.append(f"{name} had {len(meals)} meal{'s' if len(meals) != 1 else ''}: {', '.join(meals)}.")

        if "nap" in by_type:
            nap_count = len(by_type["nap"])
            nap_str = f"{total_nap_min} minutes" if total_nap_min else f"{nap_count} nap{'s' if nap_count != 1 else ''}"
            lines.append(f"{name} napped for {nap_str}.")

        if "diaper" in by_type:
            dc = len(by_type["diaper"])
            lines.append(f"Diaper changes: {dc}.")

        other_types = [t for t in by_type if t not in ("meal", "nap", "diaper")]
        for t in other_types:
            items = by_type[t]
            label = {"play": "played", "learning": "worked on", "outdoor": "enjoyed outdoor time with"}.get(t, "did")
            lines.append(f"{name} {label} {', '.join(items)}.")

        if overall_mood:
            mood_phrases = {
                "happy": f"{name} was in great spirits today! 😊",
                "energetic": f"{name} had lots of energy today! ⚡",
                "tired": f"{name} seemed a bit tired today. 😴",
                "sad": f"{name} had a tough day emotionally — we gave extra comfort. 💛",
                "cranky": f"{name} was a little cranky today — could be teething or tiredness.",
                "neutral": f"{name} had a calm, steady day.",
            }
            lines.append(mood_phrases.get(overall_mood, f"Overall mood: {overall_mood}."))

    lines.append("We look forward to seeing you tomorrow!")
    summary_text = " ".join(lines)

    return {
        "summary_text": summary_text,
        "activities_summary": activities_summary,
        "overall_mood": overall_mood,
    }
