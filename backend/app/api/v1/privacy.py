from typing import List
from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.governance import UserConsent, GovernancePolicy
from app.models.audit import AuditLog
from app.models.enums import AuditAction, ConsentStatus
from app.api.deps import get_current_user
from app.schemas.governance import UserConsentUpdate, UserConsentResponse

router = APIRouter()

@router.get("/consent", response_model=List[UserConsentResponse], summary="Get Current User's Consents")
def get_my_consents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    consents = db.query(UserConsent).filter(UserConsent.user_id == current_user.id).all()
    
    # Audit logging
    ip_address = request.client.host if request and request.client else None
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_OWN_CONSENT.value,
        resource_id=current_user.id,
        resource_type="USER_CONSENT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    return consents

@router.patch("/consent", response_model=UserConsentResponse, summary="Update Current User's Consent")
def update_my_consent(
    consent_in: UserConsentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    consent = db.query(UserConsent).filter(
        UserConsent.user_id == current_user.id,
        UserConsent.purpose == consent_in.purpose.value
    ).first()

    # Get active policy version for record
    policy = db.query(GovernancePolicy).filter(
        GovernancePolicy.organization_id == current_user.organization_id,
        GovernancePolicy.is_active == True
    ).first()
    policy_version = policy.version if policy else "unknown"

    if not consent:
        consent = UserConsent(
            user_id=current_user.id,
            purpose=consent_in.purpose.value,
            status=consent_in.status.value,
            policy_version=policy_version
        )
        db.add(consent)
    else:
        consent.status = consent_in.status.value
        consent.policy_version = policy_version

    # Audit logging
    ip_address = request.client.host if request and request.client else None
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.UPDATE_CONSENT.value,
        resource_id=current_user.id,
        resource_type="USER_CONSENT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()
    db.refresh(consent)

    return consent
