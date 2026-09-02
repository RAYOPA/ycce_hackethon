import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, AuditLog
from app.models.enums import UserRole, UserStatus, AuditAction
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_analytics_sec_db():
    db = TestingSessionLocal()

    org_a = Organization(organization_code="ORG_AN_SEC_A", name="Org Alpha")
    org_b = Organization(organization_code="ORG_AN_SEC_B", name="Org Beta")
    db.add_all([org_a, org_b])
    db.commit()

    u_a1 = Unit(organization_id=org_a.id, unit_code="U_A1", unit_name="Unit A1")
    u_a2 = Unit(organization_id=org_a.id, unit_code="U_A2", unit_name="Unit A2")
    u_b1 = Unit(organization_id=org_b.id, unit_code="U_B1", unit_name="Unit B1")
    db.add_all([u_a1, u_a2, u_b1])
    db.commit()

    personnel_a = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="P_SEC_A",
        name="Personnel Alpha",
        email="p_sec_a@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    admin_a = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="ADM_SEC_A",
        name="Admin Alpha",
        email="adm_sec_a@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMINISTRATOR,
        status=UserStatus.ACTIVE
    )
    welfare_scoped = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="W_SEC_A1",
        name="Welfare Scoped A1",
        email="w_sec_a1@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    commander_b = User(
        organization_id=org_b.id,
        unit_id=None,
        user_code="CMD_SEC_B",
        name="Commander Beta",
        email="cmd_sec_b@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    db.add_all([personnel_a, admin_a, welfare_scoped, commander_b])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_personnel_forbidden_from_all_analytics(setup_analytics_sec_db):
    token = get_token("p_sec_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/analytics/workload", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/analytics/units", headers=headers).status_code == 403

def test_admin_forbidden_from_welfare_analytics(setup_analytics_sec_db):
    token = get_token("adm_sec_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/analytics/workload", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/analytics/units", headers=headers).status_code == 403

def test_welfare_officer_unit_scope_enforcement(setup_analytics_sec_db):
    token = get_token("w_sec_a1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    u_a2 = db.query(Unit).filter(Unit.unit_code == "U_A2").first()
    db.close()

    # Welfare officer assigned to U_A1 cannot query U_A2 analytics
    res = client.get(f"{settings.API_V1_STR}/analytics/wellness?unit_id={u_a2.id}", headers=headers)
    assert res.status_code == 403

def test_cross_organization_analytics_isolation(setup_analytics_sec_db):
    token_b = get_token("cmd_sec_b@example.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # Commander B querying analytics gets Org B's data only
    res = client.get(f"{settings.API_V1_STR}/analytics/units", headers=headers_b)
    assert res.status_code == 200
    data = res.json()
    unit_names = [u["unit_name"] for u in data["units"]]
    assert "Unit B1" in unit_names
    assert "Unit A1" not in unit_names
    assert "Unit A2" not in unit_names

def test_analytics_audit_logged(setup_analytics_sec_db):
    token_b = get_token("cmd_sec_b@example.com")
    headers_b = {"Authorization": f"Bearer {token_b}"}

    client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=headers_b)
    client.get(f"{settings.API_V1_STR}/analytics/workload", headers=headers_b)

    db = TestingSessionLocal()
    cmd_b = db.query(User).filter(User.email == "cmd_sec_b@example.com").first()
    logs = db.query(AuditLog).filter(AuditLog.user_id == cmd_b.id).all()
    actions = [l.action for l in logs]
    db.close()

    assert AuditAction.VIEW_WELLNESS_ANALYTICS in actions
    assert AuditAction.VIEW_WORKLOAD_ANALYTICS in actions
