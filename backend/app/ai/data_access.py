from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.wellness import WellnessCheckin
from app.models.enums import ProcessingPurpose, AuditAction
from app.models.audit import AuditLog
from app.ai.privacy import verify_processing_purpose
from app.api.deps import get_current_user

def get_ai_eligible_personal_history(
    db: Session,
    personnel_id: str,
    purpose: ProcessingPurpose,
    current_user: User
) -> List[Dict[str, Any]]:
    """
    Safely retrieves a user's historical wellness data for AI processing.
    Enforces privacy, purpose limitation, and strips PII.
    """
    # 1. Enforce RBAC / Organization Scope
    # We must only allow accessing this if:
    # A) The user is fetching their own data
    # B) The user is a Welfare Officer in the same unit (if we allow them to run AI tools)
    # C) It's a system process (not currently supported via this function directly without a current_user)
    # For now, to be strictly safe: only the user themselves can trigger their personal AI baseline,
    # or a welfare officer in their unit if the policy permits. 
    # Let's enforce that only the personnel themselves can fetch their AI data in V1 AI foundation.
    if current_user.id != personnel_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI data access is currently restricted to the individual personnel."
        )

    # 2. Verify Consent and Governance Policy
    target_user = db.query(User).filter(User.id == personnel_id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    is_permitted = verify_processing_purpose(db, target_user, purpose)
    if not is_permitted:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Data access denied for purpose: {purpose.value}. Consent withdrawn or policy restricts."
        )

    # 3. Fetch Data
    records = db.query(WellnessCheckin).filter(
        WellnessCheckin.personnel_id == personnel_id
    ).order_by(WellnessCheckin.checkin_date.asc()).all()

    # 4. Data Minimization (Strip PII & Notes)
    ai_safe_records = []
    for r in records:
        ai_safe_records.append({
            "checkin_date": r.checkin_date.isoformat() if hasattr(r.checkin_date, "isoformat") else r.checkin_date,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "sleep_hours": r.sleep_hours,
            "sleep_quality": r.sleep_quality,
            "mood_score": r.mood_score,
            "energy_score": r.energy_score,
            "workload_score": r.workload_score,
            "stress_score": r.stress_score
        })

    # 5. Audit Logging (Do not log sensitive payload)
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.ACCESS_AI_BASELINE.value,
        resource_id=personnel_id,
        resource_type="USER_AI_DATA",
        ip_address="internal_ai_service"
    )
    db.add(audit)
    db.commit()

    return ai_safe_records
