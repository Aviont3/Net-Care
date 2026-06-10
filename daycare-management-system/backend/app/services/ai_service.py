"""AI Service — generates daily reports for parents.

Supports two modes:
  - Template-based (default): deterministic, no external calls.
  - LLM-powered (use_llm=True): GPT-4 narrative via OpenAI API with PII
    redaction, rate limiting, tone control, and automatic fallback.

Issue #37: GPT-4 narrative report generation.
"""

import logging
import re
from collections import Counter
from datetime import date, datetime
from typing import Literal, Optional
from uuid import UUID

from openai import AsyncOpenAI, OpenAIError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.child import Child
from app.models.daily_operations import Activity, Attendance
from app.models.health_safety import IncidentReport

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rate Limiting (in-memory; swap with Redis for multi-process deployments)
# ---------------------------------------------------------------------------

_rate_limit_store: dict[str, dict[str, int]] = {}
_DAILY_LLM_LIMIT_PER_CENTER = 50


def _check_rate_limit(center_id: str) -> bool:
    """Return True if the center is within its daily LLM report quota."""
    today = date.today().isoformat()
    if center_id not in _rate_limit_store:
        _rate_limit_store[center_id] = {}
    center_usage = _rate_limit_store[center_id]

    # Reset if it's a new day
    if today not in center_usage:
        _rate_limit_store[center_id] = {today: 0}
        center_usage = _rate_limit_store[center_id]

    return center_usage[today] < _DAILY_LLM_LIMIT_PER_CENTER


def _increment_rate_limit(center_id: str) -> None:
    """Record one LLM report usage for the center today."""
    today = date.today().isoformat()
    _rate_limit_store.setdefault(center_id, {}).setdefault(today, 0)
    _rate_limit_store[center_id][today] += 1


# ---------------------------------------------------------------------------
# PII Redaction
# ---------------------------------------------------------------------------

# Patterns to strip before sending data to the LLM
_PHONE_RE = re.compile(
    r"(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)
_EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)
_ADDRESS_RE = re.compile(
    r"\d{1,5}\s[\w\s]{1,50}(?:Street|St|Avenue|Ave|Boulevard|Blvd|Drive|Dr|"
    r"Lane|Ln|Road|Rd|Court|Ct|Way|Place|Pl)\.?(?:\s*,?\s*\w+,?\s*[A-Z]{2}\s*\d{5})?",
    re.IGNORECASE,
)
_SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def _redact_pii(text: str, *, preserve_first_names: list[str] | None = None) -> str:
    """Remove PII from text before LLM processing.

    - Strips phone numbers, emails, addresses, SSN-like patterns.
    - Strips last names (anything that looks like "FirstName LastName").
    - Preserves explicitly allowed first names.
    """
    text = _PHONE_RE.sub("[PHONE]", text)
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _ADDRESS_RE.sub("[ADDRESS]", text)
    text = _SSN_RE.sub("[SSN]", text)

    # Remove standalone last-name patterns (e.g., "signed by Jane Smith" -> "signed by Jane [REDACTED]")
    # We apply a heuristic: capitalized word following a known first name
    if preserve_first_names:
        for first in preserve_first_names:
            # Pattern: first_name followed by a capitalized word (potential last name)
            pattern = re.compile(
                rf"\b({re.escape(first)})\s+([A-Z][a-z]+(?:[-'][A-Z][a-z]+)?)\b"
            )
            text = pattern.sub(rf"\1 [REDACTED]", text)

    return text


def _redact_dict(data: dict, preserve_first_names: list[str] | None = None) -> dict:
    """Recursively redact string values in a dictionary."""
    redacted = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted[key] = _redact_pii(value, preserve_first_names=preserve_first_names)
        elif isinstance(value, dict):
            redacted[key] = _redact_dict(value, preserve_first_names=preserve_first_names)
        elif isinstance(value, list):
            redacted[key] = [
                _redact_dict(item, preserve_first_names=preserve_first_names)
                if isinstance(item, dict)
                else _redact_pii(item, preserve_first_names=preserve_first_names)
                if isinstance(item, str)
                else item
                for item in value
            ]
        else:
            redacted[key] = value
    return redacted


# ---------------------------------------------------------------------------
# LLM Prompt Construction
# ---------------------------------------------------------------------------

_SYSTEM_PROMPTS: dict[str, str] = {
    "warm": (
        "You are a loving daycare teacher writing a daily report for a parent. "
        "Your tone is warm, cheerful, and personal. Use the child's first name "
        "frequently. Add relevant emojis sparingly. Make the parent feel connected "
        "to their child's day."
    ),
    "professional": (
        "You are a daycare professional writing a concise daily report for a parent. "
        "Your tone is clear, organized, and reassuring. Use the child's first name. "
        "Focus on facts and developmental observations."
    ),
    "brief": (
        "You are a daycare teacher writing a very brief daily summary for a parent. "
        "Keep it under 4 sentences. Mention the child's first name, key highlights, "
        "and overall mood. Be friendly but concise."
    ),
}


def _build_activity_context(
    child: Child,
    activities: list[Activity],
    attendance: Optional[Attendance],
    incidents: list[IncidentReport],
    report_date: date,
) -> str:
    """Build a structured text block describing the child's day for the LLM prompt."""
    lines = [f"Child's first name: {child.first_name}"]
    lines.append(f"Date: {report_date.strftime('%A, %B %d, %Y')}")

    if attendance:
        if attendance.check_in_time:
            lines.append(f"Arrived: {attendance.check_in_time.strftime('%-I:%M %p')}")
        if attendance.check_out_time:
            lines.append(f"Picked up: {attendance.check_out_time.strftime('%-I:%M %p')}")

    # Group activities
    by_type: dict[str, list[dict]] = {}
    moods: list[str] = []
    for a in activities:
        entry = {"name": a.activity_name, "time": a.activity_time.strftime("%-I:%M %p")}
        if a.duration_minutes:
            entry["duration_min"] = a.duration_minutes
        if a.description:
            entry["description"] = a.description
        if a.notes:
            entry["notes"] = a.notes
        if a.mood:
            moods.append(a.mood)
            entry["mood"] = a.mood
        by_type.setdefault(a.activity_type, []).append(entry)

    if by_type.get("meal"):
        lines.append(f"\nMeals ({len(by_type['meal'])}):")
        for m in by_type["meal"]:
            lines.append(f"  - {m['time']}: {m['name']}")

    if by_type.get("nap"):
        total_nap = sum(n.get("duration_min", 0) for n in by_type["nap"])
        lines.append(f"\nNaps ({len(by_type['nap'])}, total {total_nap} min):")
        for n in by_type["nap"]:
            dur = f" ({n['duration_min']} min)" if n.get("duration_min") else ""
            lines.append(f"  - {n['time']}: {n['name']}{dur}")

    if by_type.get("diaper"):
        lines.append(f"\nDiaper changes: {len(by_type['diaper'])}")

    other_types = [t for t in by_type if t not in ("meal", "nap", "diaper")]
    for t in other_types:
        lines.append(f"\n{t.capitalize()} activities ({len(by_type[t])}):")
        for item in by_type[t]:
            desc = f" — {item['description']}" if item.get("description") else ""
            lines.append(f"  - {item['time']}: {item['name']}{desc}")

    if moods:
        mood_counter = Counter(moods)
        mood_summary = ", ".join(f"{mood} ({count}x)" for mood, count in mood_counter.most_common())
        lines.append(f"\nMood observations throughout the day: {mood_summary}")

    if incidents:
        lines.append(f"\nIncidents ({len(incidents)}):")
        for inc in incidents:
            lines.append(
                f"  - [{inc.incident_type}] at {inc.incident_time.strftime('%-I:%M %p')}: "
                f"{inc.description}. Action taken: {inc.action_taken}"
            )

    if not activities and not incidents:
        lines.append("\nNo activities or incidents were logged today.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# OpenAI Client (lazy singleton)
# ---------------------------------------------------------------------------

_openai_client: Optional[AsyncOpenAI] = None


def _get_openai_client() -> AsyncOpenAI:
    """Return a cached AsyncOpenAI client instance."""
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


# ---------------------------------------------------------------------------
# LLM Report Generation
# ---------------------------------------------------------------------------


async def _generate_llm_report(
    db: Session,
    child_id: UUID,
    report_date: date,
    tone: Literal["warm", "professional", "brief"] = "warm",
    center_id: str = "default",
) -> dict:
    """Generate a GPT-4 powered narrative daily report.

    Includes PII redaction, rate limiting, and automatic fallback to templates.
    """
    # --- Rate limit check ---
    if not _check_rate_limit(center_id):
        logger.warning(
            "LLM rate limit reached for center %s (%d/day). Falling back to template.",
            center_id,
            _DAILY_LLM_LIMIT_PER_CENTER,
        )
        return _generate_template_report(db, child_id, report_date)

    # --- Fetch data ---
    child = db.query(Child).filter(Child.id == child_id).first()
    if not child:
        raise ValueError(f"Child {child_id} not found")

    activities = (
        db.query(Activity)
        .filter(Activity.child_id == child_id, Activity.activity_date == report_date)
        .order_by(Activity.activity_time)
        .all()
    )

    attendance = (
        db.query(Attendance)
        .filter(Attendance.child_id == child_id, Attendance.attendance_date == report_date)
        .first()
    )

    incidents = (
        db.query(IncidentReport)
        .filter(IncidentReport.child_id == child_id, IncidentReport.incident_date == report_date)
        .all()
    )

    # --- Build context and redact PII ---
    raw_context = _build_activity_context(child, activities, attendance, incidents, report_date)
    redacted_context = _redact_pii(raw_context, preserve_first_names=[child.first_name])

    # --- Build prompt ---
    system_prompt = _SYSTEM_PROMPTS.get(tone, _SYSTEM_PROMPTS["warm"])
    user_prompt = (
        f"Write a daily report for {child.first_name}'s parent based on this data:\n\n"
        f"{redacted_context}\n\n"
        "Guidelines:\n"
        "- Address the parent directly (e.g., 'Hi there!' or 'Hello!')\n"
        "- Mention all meals, naps, and key activities naturally\n"
        "- If there were incidents, describe them gently but honestly\n"
        "- End with a positive, forward-looking note\n"
        "- Do NOT include any PII, last names, phone numbers, or addresses\n"
        "- Keep the report to 1-2 short paragraphs unless there's a lot to cover"
    )

    # --- Call OpenAI ---
    try:
        client = _get_openai_client()
        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=500,
        )
        narrative = response.choices[0].message.content.strip()

        # Final safety pass: redact any PII the model might have hallucinated
        narrative = _redact_pii(narrative, preserve_first_names=[child.first_name])

        _increment_rate_limit(center_id)
        logger.info(
            "LLM report generated for child %s on %s (center=%s, tone=%s)",
            child_id,
            report_date,
            center_id,
            tone,
        )

    except OpenAIError as e:
        logger.error(
            "OpenAI API error generating report for child %s: %s. Falling back to template.",
            child_id,
            str(e),
        )
        return _generate_template_report(db, child_id, report_date)
    except Exception as e:
        logger.exception(
            "Unexpected error during LLM report generation for child %s. Falling back to template.",
            child_id,
        )
        return _generate_template_report(db, child_id, report_date)

    # --- Build structured summary (same as template mode for consistency) ---
    by_type: dict[str, list[str]] = {}
    moods: list[str] = []
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
        "incident_count": len(incidents),
    }

    return {
        "summary_text": narrative,
        "activities_summary": activities_summary,
        "overall_mood": overall_mood,
        "generation_mode": "llm",
        "tone": tone,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_report(
    db: Session,
    child_id: UUID,
    report_date: date,
    use_llm: bool = False,
    tone: Literal["warm", "professional", "brief"] = "warm",
    center_id: str = "default",
) -> dict:
    """Generate a daily report for a child.

    Args:
        db: Database session.
        child_id: UUID of the child.
        report_date: Date of the report.
        use_llm: If True, use GPT-4 to generate a narrative report.
                 Defaults to False (template mode).
        tone: Narrative tone when using LLM. One of "warm", "professional", "brief".
        center_id: Center identifier for rate limiting (max 50 LLM reports/day per center).

    Returns:
        dict with keys: summary_text, activities_summary, overall_mood,
        and (when LLM) generation_mode, tone.
    """
    if use_llm:
        return await _generate_llm_report(db, child_id, report_date, tone=tone, center_id=center_id)

    result = _generate_template_report(db, child_id, report_date)
    result["generation_mode"] = "template"
    return result


def generate_report_sync(
    db: Session,
    child_id: UUID,
    report_date: date,
) -> dict:
    """Synchronous template-only report generation (backwards-compatible).

    Use this in contexts where async is not available. Does not support LLM mode.
    """
    result = _generate_template_report(db, child_id, report_date)
    result["generation_mode"] = "template"
    return result


# ---------------------------------------------------------------------------
# Template Report (original implementation preserved)
# ---------------------------------------------------------------------------


def _generate_template_report(db: Session, child_id: UUID, report_date: date) -> dict:
    """Generate a deterministic template-based daily report."""
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
