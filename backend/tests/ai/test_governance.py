import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models.user import User
from app.models.enums import UserRole, UserStatus, ProcessingPurpose, ConsentStatus
from tests.conftest import TestingSessionLocal
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.unit import Unit

client = TestClient(app)

@pytest.fixture
def setup_db():
    db = TestingSessionLocal()
    import uuid
    suffix = str(uuid.uuid4())[:8]
    org = Organization(organization_code=f"ORG_GOV_{suffix}", name="Gov Org")
    db.add(org)
    db.commit()
    unit = Unit(organization_id=org.id, unit_name="Gov Unit", unit_code=f"UNIT_{suffix}")
    db.add(unit)
    db.commit()
    p_a1 = User(
        organization_id=org.id, unit_id=unit.id, user_code=f"PA_{suffix}", name="PA GOV1",
        email=f"pa1_{suffix}@example.com", password_hash=get_password_hash("password123"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE
    )
    adma1 = User(
        organization_id=org.id, unit_id=unit.id, user_code=f"ADM_{suffix}", name="ADM GOV1",
        email=f"adma1_{suffix}@example.com", password_hash=get_password_hash("password123"), role=UserRole.ADMINISTRATOR, status=UserStatus.ACTIVE
    )
    db.add_all([p_a1, adma1])
    db.commit()
    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_get_own_consent(setup_db):
    email = setup_db.query(User).filter(User.role == UserRole.PERSONNEL).first().email
    token = get_token(email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # User should have no consent by default initially unless set
    res = client.get(f"{settings.API_V1_STR}/privacy/consent", headers=headers)
    assert res.status_code == 200
    assert len(res.json()) == 0

def test_update_own_consent(setup_db):
    email = setup_db.query(User).filter(User.role == UserRole.PERSONNEL).first().email
    token = get_token(email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Grant consent for AI_BASELINE
    res = client.patch(
        f"{settings.API_V1_STR}/privacy/consent",
        json={"purpose": "AI_BASELINE", "status": "GRANTED"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["purpose"] == "AI_BASELINE"
    assert data["status"] == "GRANTED"

def test_admin_manage_governance(setup_db):
    email = setup_db.query(User).filter(User.role == UserRole.ADMINISTRATOR).first().email
    token = get_token(email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Read governance policy (creates default if missing)
    res = client.get(f"{settings.API_V1_STR}/admin/governance", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "WELLNESS_SUPPORT" in data["allowed_purposes"]
    
    # Update governance policy to allow AI
    res_patch = client.patch(
        f"{settings.API_V1_STR}/admin/governance",
        json={
            "allowed_purposes": ["WELLNESS_SUPPORT", "ANALYTICS", "AI_BASELINE", "AI_PREDICTION"],
            "is_active": True
        },
        headers=headers
    )
    assert res_patch.status_code == 200
    data_patch = res_patch.json()
    assert "AI_BASELINE" in data_patch["allowed_purposes"]
