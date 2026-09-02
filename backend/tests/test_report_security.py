import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, AuditLog
from app.models.enums import UserRole, UserStatus, AuditAction
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_report_sec_db():
    db = TestingSessionLocal()

    org_a = Organization(organization_code="ORG_REP_SEC_A", name="Report Org Alpha")
    org_b = Organization(organization_code="ORG_REP_SEC_B", name="Report Org Beta")
    db.add_all([org_a, org_b])
    db.commit()

    u_a1 = Unit(organization_id=org_a.id, unit_code="U_REP_A1", unit_name="Unit Rep A1")
    u_a2 = Unit(organization_id=org_a.id, unit_code="U_REP_A2", unit_name="Unit Rep A2")
    u_b1 = Unit(organization_id=org_b.id, unit_code="U_REP_B1", unit_name="Unit Rep B1")
    db.add_all([u_a1, u_a2, u_b1])
    db.commit()

    personnel_a = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="P_REP_A",
        name="Personnel Rep A",
        email="p_rep_a@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    admin_a = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="ADM_REP_A",
        name="Admin Rep A",
        email="adm_rep_a@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMINISTRATOR,
        status=UserStatus.ACTIVE
    )
    commander_a = User(
        organization_id=org_a.id,
        unit_id=None,
        user_code="CMD_REP_A",
        name="Commander Rep A",
        email="cmd_rep_a@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    welfare_scoped_a1 = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="W_REP_A1",
        name="Welfare Rep A1",
        email="w_rep_a1@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    inactive_user = User(
        organization_id=org_a.id,
        unit_id=u_a1.id,
        user_code="INACT_REP",
        name="Inactive Rep",
        email="inact_rep@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.INACTIVE
    )
    db.add_all([personnel_a, admin_a, commander_a, welfare_scoped_a1, inactive_user])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_personnel_forbidden_from_reports_and_exports(setup_report_sec_db):
    token = get_token("p_rep_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"{settings.API_V1_STR}/reports/wellness", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/workload", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/units", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/welfare-activity", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/wellness/export", headers=headers).status_code == 403

def test_admin_forbidden_from_welfare_reports(setup_report_sec_db):
    token = get_token("adm_rep_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get(f"{settings.API_V1_STR}/reports/wellness", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/welfare-activity", headers=headers).status_code == 403
    assert client.get(f"{settings.API_V1_STR}/reports/wellness/export", headers=headers).status_code == 403

def test_welfare_officer_unit_scope_enforcement(setup_report_sec_db):
    token = get_token("w_rep_a1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    u_a2 = db.query(Unit).filter(Unit.unit_code == "U_REP_A2").first()
    db.close()

    # Officer scoped to A1 cannot request report for A2
    res = client.get(f"{settings.API_V1_STR}/reports/wellness?unit_id={u_a2.id}", headers=headers)
    assert res.status_code == 403

def test_cross_organization_unit_rejected(setup_report_sec_db):
    token = get_token("cmd_rep_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    u_b1 = db.query(Unit).filter(Unit.unit_code == "U_REP_B1").first()
    db.close()

    # Commander A querying Unit B1 in Org B -> 404 (Unit not found in your organization)
    res = client.get(f"{settings.API_V1_STR}/reports/wellness?unit_id={u_b1.id}", headers=headers)
    assert res.status_code == 404

def test_inactive_user_cannot_login_or_access(setup_report_sec_db):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "inact_rep@example.com", "password": "password123"}
    )
    assert res.status_code == 401

def test_report_and_export_audit_logged(setup_report_sec_db):
    token = get_token("cmd_rep_a@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    client.get(f"{settings.API_V1_STR}/reports/wellness", headers=headers)
    client.get(f"{settings.API_V1_STR}/reports/wellness/export?format=csv", headers=headers)

    db = TestingSessionLocal()
    cmd = db.query(User).filter(User.email == "cmd_rep_a@example.com").first()
    logs = db.query(AuditLog).filter(AuditLog.user_id == cmd.id).all()
    actions = [l.action for l in logs]
    db.close()

    assert AuditAction.VIEW_WELLNESS_REPORT in actions
    assert AuditAction.EXPORT_WELLNESS_REPORT in actions
