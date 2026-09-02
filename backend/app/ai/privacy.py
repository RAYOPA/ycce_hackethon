from sqlalchemy.orm import Session
from app.models.governance import GovernancePolicy, UserConsent
from app.models.enums import ProcessingPurpose, ConsentStatus
from app.models.user import User

def verify_processing_purpose(db: Session, user: User, purpose: ProcessingPurpose) -> bool:
    """
    Verifies if a specific processing purpose is permitted for a given user.
    1. Checks if the user's organization governance policy allows the purpose.
    2. Checks if the user has explicitly GRANTED consent for that purpose.
    """
    # 1. Organization Governance Policy Check
    policy = db.query(GovernancePolicy).filter(
        GovernancePolicy.organization_id == user.organization_id,
        GovernancePolicy.is_active == True
    ).first()

    if not policy or purpose.value not in policy.allowed_purposes:
        return False
        
    # 2. Individual User Consent Check
    consent = db.query(UserConsent).filter(
        UserConsent.user_id == user.id,
        UserConsent.purpose == purpose.value
    ).first()

    if not consent or consent.status != ConsentStatus.GRANTED.value:
        return False
        
    return True
