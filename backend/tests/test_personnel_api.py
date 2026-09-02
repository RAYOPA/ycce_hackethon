import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_personnel_db():
    db = TestingSessionLocal()

    org1 = Organization(organization_code="ORG_P1", name="Alpha Command")
    org2 = Organization(organization_code="ORG_P2", name="Beta Command")
    db.add_all([org1, org2])
    db.commit()

    unit1 = Unit(organization_id=org1.id, unit_code="UNIT_P1", unit_name="Alpha Unit")
    unit2 = Unit(organization_id=org2.id, unit_code="UNIT_P2", unit_name="Beta Unit")
    db.add_all([unit1, unit2])
    db.commit()

    p1 = User(
        organization_id=org1.id,
        unit_id=unit1.id,
        user_code="P_P001",
        name="Personnel One",
        email="p1_p@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    p2 = User(
        organization_id=org1.id,
        unit_id=unit1.id,
        user_code="P_P002",
        name="Personnel Two",
        email="p2_p@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w1 = User(
        organization_id=org1.id,
        unit_id=unit1.id,
        user_code="W_P001",
        name="Welfare Officer One",
        email="w1_p@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    c1 = User(
        organization_id=org1.id,
        unit_id=unit1.id,
        user_code="C_P001",
        name="Commander One",
        email="c1_p@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    p_org2 = User(
        organization_id=org2.id,
        unit_id=unit2.id,
        user_code="P_PORG2",
        name="Personnel Beta",
        email="p_org2_p@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    db.add_all([p1, p2, w1, c1, p_org2])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_personnel_me_success(setup_personnel_db):
    token = get_token("p1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{settings.API_V1_STR}/personnel/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "p1_p@example.com"
    assert data["user_code"] == "P_P001"
    assert data["name"] == "Personnel One"
    assert "password_hash" not in data

def test_personnel_cannot_list_all_personnel(setup_personnel_db):
    token = get_token("p1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{settings.API_V1_STR}/personnel", headers=headers)
    assert res.status_code == 403

def test_welfare_officer_can_list_personnel(setup_personnel_db):
    token = get_token("w1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{settings.API_V1_STR}/personnel", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    # P_P001 and P_P002 in org 1
    assert data["total"] == 2

def test_personnel_cannot_view_other_personnel_profile(setup_personnel_db):
    token = get_token("p1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p2 = db.query(User).filter(User.email == "p2_p@example.com").first()
    res = client.get(f"{settings.API_V1_STR}/personnel/{p2.id}", headers=headers)
    db.close()
    assert res.status_code == 403

def test_commander_cannot_view_individual_personnel_profile(setup_personnel_db):
    token = get_token("c1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p1 = db.query(User).filter(User.email == "p1_p@example.com").first()
    res = client.get(f"{settings.API_V1_STR}/personnel/{p1.id}", headers=headers)
    db.close()
    assert res.status_code == 403

def test_cross_org_personnel_not_found(setup_personnel_db):
    token = get_token("w1_p@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_org2 = db.query(User).filter(User.email == "p_org2_p@example.com").first()
    res = client.get(f"{settings.API_V1_STR}/personnel/{p_org2.id}", headers=headers)
    db.close()
    assert res.status_code == 404
