"""
AI Privacy Firewall — Purpose-limited payload builder.

CRITICAL: Every piece of data sent to the AI provider MUST pass through this
module first.  The firewall enforces the principle of data minimisation:

    FastAPI → Privacy Firewall → Purpose-limited AI payload → OpenRouter

WHAT IS STRIPPED:
- Password hashes
- JWT / refresh tokens / API keys
- Internal security information
- Unnecessary PII (names, email, mobile, address)
- Unrelated personnel records
- Other personnel's data
- Unauthorized welfare notes
- Unauthorized administrative data

The external AI provider receives ONLY the minimum data required for the
specific task being performed.

NOTE on pseudonymisation:
For welfare reports, a pseudonymous Case ID (e.g. MR-7F29K4) replaces
the personnel identity.  The identity mapping is maintained INSIDE
ManRakshak and is never sent to the AI provider.
"""

import random
import string
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.ai.features import get_temporal_features
from app.models.enums import UserRole
from app.models.user import User
from app.models.wellness import WellnessCheckin


# ---------------------------------------------------------------------------
# Permitted AI payload fields — whitelist approach
# ---------------------------------------------------------------------------

# Wellness fields safe to include in AI payloads (no PII, no security fields)
_WELLNESS_SAFE_FIELDS = {
    "checkin_date",
    "sleep_hours",
    "sleep_quality",
    "mood_score",
    "energy_score",
    "workload_score",
    "stress_score",
}

# Personnel fields explicitly FORBIDDEN from AI payloads
_FORBIDDEN_PERSONNEL_FIELDS = {
    "password_hash",
    "email",
    "mobile_number",
    "address",
    "name",         # Replaced by pseudonymous case_id in reports
    "user_code",    # Internal identifier — not needed by AI
}


# ---------------------------------------------------------------------------
# RBAC enforcement for AI endpoints
# ---------------------------------------------------------------------------

def enforce_ai_access_policy(
    current_user: User,
    target_personnel_id: str,
    db: Session,
) -> User:
    """
    Enforce who can trigger AI analysis on whose data.

    Rules:
    - PERSONNEL: Can only request AI analysis of their OWN data.
    - WELFARE_OFFICER: Can request AI analysis of personnel in their organisation.
    - COMMANDER: Cannot access individual protected AI wellness data.
    - ADMINISTRATOR: Cannot automatically gain protected welfare AI access.

    Returns the target User object (for downstream use).
    Raises HTTP 403 on violation.
    """
    target_user = db.query(User).filter(
        User.id == target_personnel_id,
        User.organization_id == current_user.organization_id,
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnel not found within your organisation.",
        )

    if current_user.role == UserRole.PERSONNEL:
        if current_user.id != target_personnel_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Personnel can only request AI analysis of their own data.",
            )

    elif current_user.role == UserRole.COMMANDER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Privacy violation: Commanders cannot access individual protected "
                "AI wellness data."
            ),
        )

    elif current_user.role == UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Privacy violation: Administrators do not automatically gain "
                "protected welfare AI access."
            ),
        )

    # WELFARE_OFFICER: permitted (organisation isolation enforced by the query above)
    return target_user


# ---------------------------------------------------------------------------
# Wellness evidence builder
# ---------------------------------------------------------------------------

def build_wellness_evidence_payload(
    db: Session,
    personnel_id: str,
    assessment_period_days: int = 30,
) -> Dict[str, Any]:
    """
    Query the database and build a purpose-limited wellness evidence payload
    suitable for sending to the AI provider.

    - Strips ALL PII and security fields.
    - Uses only numeric wellness metrics.
    - Computes all baselines and trends DETERMINISTICALLY in the backend.
    - The AI receives numbers and metadata — not raw DB records.
    """
    # Fetch records ordered oldest → newest
    records = (
        db.query(WellnessCheckin)
        .filter(WellnessCheckin.personnel_id == personnel_id)
        .order_by(WellnessCheckin.checkin_date.asc())
        .all()
    )

    if not records:
        return {
            "assessment_period_days": assessment_period_days,
            "data_quality": "no_data",
            "history_length": 0,
            "signals": {},
            "note": "No wellness check-in data available.",
        }

    # Convert to PII-free dicts
    safe_records = [
        {
            "checkin_date": str(r.checkin_date),
            "sleep_hours": r.sleep_hours,
            "sleep_quality": r.sleep_quality,
            "mood_score": r.mood_score,
            "energy_score": r.energy_score,
            "workload_score": r.workload_score,
            "stress_score": r.stress_score,
        }
        for r in records
    ]

    # Compute recent window
    recent = safe_records[-assessment_period_days:] if len(safe_records) > assessment_period_days else safe_records

    # Backend-computed signals (AI must not recalculate)
    signals: Dict[str, Any] = {}
    signal_names = ["sleep_hours", "sleep_quality", "mood_score", "energy_score", "workload_score", "stress_score"]

    for sig in signal_names:
        all_vals = [r[sig] for r in safe_records if r.get(sig) is not None]
        recent_vals = [r[sig] for r in recent if r.get(sig) is not None]

        if not all_vals:
            signals[sig] = {"data_quality": "no_data"}
            continue

        baseline = sum(all_vals) / len(all_vals) if all_vals else None
        recent_avg = sum(recent_vals) / len(recent_vals) if recent_vals else None

        # Simple trend: positive = increasing, negative = decreasing
        trend_label = "stable"
        if len(all_vals) >= 5:
            first_half = all_vals[: len(all_vals) // 2]
            second_half = all_vals[len(all_vals) // 2 :]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            diff = second_avg - first_avg
            if diff > 0.3:
                trend_label = "increasing"
            elif diff < -0.3:
                trend_label = "decreasing"

        signals[sig] = {
            "baseline": round(baseline, 2) if baseline is not None else None,
            "recent_average": round(recent_avg, 2) if recent_avg is not None else None,
            "trend": trend_label,
            "observation_count": len(all_vals),
        }

    data_quality = "high" if len(safe_records) >= 14 else ("moderate" if len(safe_records) >= 7 else "low")

    return {
        "assessment_period_days": assessment_period_days,
        "data_quality": data_quality,
        "history_length": len(safe_records),
        "signals": signals,
    }


# ---------------------------------------------------------------------------
# Conversation sanitiser
# ---------------------------------------------------------------------------

def sanitise_conversation_turns(
    raw_turns: List[Dict[str, str]],
) -> List[Dict[str, str]]:
    """
    Sanitise conversation turns before sending to the AI provider.

    - Strips excess whitespace.
    - Truncates individual messages to a safe maximum length.
    - Limits total number of turns.
    - Only keeps 'role' and 'content' keys (drops everything else).

    The AI provider receives sanitised content as DATA inside a clearly
    delimited block — not as executable instructions.
    """
    MAX_TURNS = 50
    MAX_CONTENT_CHARS = 2000  # per turn

    sanitised = []
    for turn in raw_turns[:MAX_TURNS]:
        role = str(turn.get("role", "user")).lower().strip()
        if role not in ("user", "assistant"):
            role = "user"
        content = str(turn.get("content", "")).strip()
        content = content[:MAX_CONTENT_CHARS]
        sanitised.append({"role": role, "content": content})

    return sanitised


# ---------------------------------------------------------------------------
# Pseudonymous Case ID generator
# ---------------------------------------------------------------------------

def generate_case_id(prefix: str = "MR") -> str:
    """
    Generate a pseudonymous Case ID for welfare report pseudonymisation.

    Format: MR-XXXXXXXX (8 uppercase alphanumeric characters)
    Example: MR-7F29K4AB

    IMPORTANT: This pseudonymises the case — it is NOT true anonymity.
    The identity mapping (case_id → personnel_id) must be maintained
    securely inside ManRakshak and NEVER sent to the AI provider.
    """
    chars = string.ascii_uppercase + string.digits
    random_part = "".join(random.choices(chars, k=8))
    return f"{prefix}-{random_part}"


# ---------------------------------------------------------------------------
# Case evidence builder (for welfare report)
# ---------------------------------------------------------------------------

def build_case_evidence_payload(
    db: Session,
    personnel_id: str,
    case_id: str,
    conversation_observations: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Build a pseudonymous, purpose-limited case evidence payload for welfare report generation.

    - Replaces personnel_id with pseudonymous case_id.
    - Includes backend-computed wellness evidence only.
    - Optionally includes structured conversation observations (NOT raw conversation).
    - Strips ALL PII from the payload.
    """
    wellness_evidence = build_wellness_evidence_payload(db, personnel_id)

    payload: Dict[str, Any] = {
        "case_id": case_id,  # Pseudonymous — identity mapping NOT included
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "wellness_evidence": wellness_evidence,
    }

    if conversation_observations:
        # Include only the structured observations — never raw conversation
        payload["conversation_observations"] = {
            "reported_stressors": conversation_observations.get("reported_stressors", []),
            "sleep_concern": conversation_observations.get("sleep_concern", False),
            "fatigue_reported": conversation_observations.get("fatigue_reported", False),
            "workload_concern": conversation_observations.get("workload_concern", False),
            "emotional_themes": conversation_observations.get("emotional_themes", []),
            "support_requested": conversation_observations.get("support_requested", False),
            "confidence": conversation_observations.get("confidence", "low"),
            "evidence_summary": conversation_observations.get("evidence_summary", ""),
        }

    return payload
