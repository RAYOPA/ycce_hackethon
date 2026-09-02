import pytest
from fastapi import HTTPException
from app.ai.data_access import get_ai_eligible_personal_history
from app.models.enums import ProcessingPurpose, UserRole
from tests.conftest import TestingSessionLocal
from app.models.user import User
from app.ai.privacy import verify_processing_purpose
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.unit import Unit
from app.models.enums import UserRole, UserStatus

@pytest.fixture
def setup_db():
    db = TestingSessionLocal()
    import uuid
    suffix = str(uuid.uuid4())[:8]
    org = Organization(organization_code=f"ORG_GOV_PRIV_{suffix}", name="Gov Org Priv")
    db.add(org)
    db.commit()
    unit = Unit(organization_id=org.id, unit_name="Gov Unit Priv", unit_code=f"UNIT_PRIV_{suffix}")
    db.add(unit)
    db.commit()
    p_a1 = User(
        organization_id=org.id, unit_id=unit.id, user_code=f"PA_GOV1_{suffix}", name="PA GOV1",
        email=f"pa1_{suffix}@example.com", password_hash=get_password_hash("password123"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE
    )
    p_a2 = User(
        organization_id=org.id, unit_id=unit.id, user_code=f"PA_GOV2_{suffix}", name="PA GOV2",
        email=f"pa2_{suffix}@example.com", password_hash=get_password_hash("password123"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE
    )
    ca1 = User(
        organization_id=org.id, unit_id=unit.id, user_code=f"CA_GOV1_{suffix}", name="CA GOV1",
        email=f"ca1_{suffix}@example.com", password_hash=get_password_hash("password123"), role=UserRole.COMMANDER, status=UserStatus.ACTIVE
    )
    db.add_all([p_a1, p_a2, ca1])
    db.commit()
    yield db
    db.close()

def test_ai_privacy_firewall_blocks_without_consent(setup_db):
    db = TestingSessionLocal()
    
    # Grab pa1 (who has no consent yet for AI_BASELINE)
    # Grab a personnel user
    pa1 = db.query(User).filter(User.name == "PA GOV1").first()
    
    # Attempting to fetch their own history for AI baseline should raise 403
    with pytest.raises(HTTPException) as exc:
        get_ai_eligible_personal_history(db, pa1.id, ProcessingPurpose.AI_BASELINE, current_user=pa1)
    
    assert exc.value.status_code == 403
    db.close()

def test_ai_privacy_firewall_blocks_cross_user(setup_db):
    db = TestingSessionLocal()
    pa1 = db.query(User).filter(User.name == "PA GOV1").first()
    pa2 = db.query(User).filter(User.name == "PA GOV2").first()
    ca1 = db.query(User).filter(User.name == "CA GOV1").first() # Commander
    
    # Cross-personnel block
    with pytest.raises(HTTPException) as exc1:
        get_ai_eligible_personal_history(db, pa1.id, ProcessingPurpose.AI_BASELINE, current_user=pa2)
    assert exc1.value.status_code == 403
    
    # Commander block
    with pytest.raises(HTTPException) as exc2:
        get_ai_eligible_personal_history(db, pa1.id, ProcessingPurpose.AI_BASELINE, current_user=ca1)
    assert exc2.value.status_code == 403
    
    db.close()
