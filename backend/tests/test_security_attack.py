import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, AuditLog
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_security_db():
    db = TestingSessionLocal()

    org_a = Organization(organization_code="ORG_SEC_A", name="Command Alpha")
    org_b = Organization(organization_code="ORG_SEC_B", name="Command Bravo")
    db.add_all([org_a, org_b])
    db.commit()

    unit_a = Unit(organization_id=org_a.id, unit_code="UNIT_SEC_A", unit_name="Alpha Unit")
    unit_b = Unit(organization_id=org_b.id, unit_code="UNIT_SEC_B", unit_name="Bravo Unit")
    db.add_all([unit_a, unit_b])
    db.commit()

    p_a1 = User(
        organization_id=org_a.id,
        unit_id=unit_a.id,
        user_code="PA01_S",
        name="Personnel Alpha 1",
        email="pa1_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    p_a2 = User(
        organization_id=org_a.id,
        unit_id=unit_a.id,
        user_code="PA02_S",
        name="Personnel Alpha 2",
        email="pa2_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w_a = User(
        organization_id=org_a.id,
        unit_id=unit_a.id,
        user_code="WA01_S",
        name="Welfare Officer Alpha",
        email="wa_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    c_a = User(
        organization_id=org_a.id,
        unit_id=unit_a.id,
        user_code="CA01_S",
        name="Commander Alpha",
        email="ca_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    adm_a = User(
        organization_id=org_a.id,
        unit_id=unit_a.id,
        user_code="ADMA01_S",
        name="Admin Alpha",
        email="adma_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMINISTRATOR,
        status=UserStatus.ACTIVE
    )

    p_b1 = User(
        organization_id=org_b.id,
        unit_id=unit_b.id,
        user_code="PB01_S",
        name="Personnel Bravo 1",
        email="pb1_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w_b = User(
        organization_id=org_b.id,
        unit_id=unit_b.id,
        user_code="WB01_S",
        name="Welfare Officer Bravo",
        email="wb_s@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )

    db.add_all([p_a1, p_a2, w_a, c_a, adm_a, p_b1, w_b])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_attack_spoof_personnel_id_in_wellness_rejected(setup_security_db):
    token = get_token("pa1_s@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_a2 = db.query(User).filter(User.email == "pa2_s@example.com").first()

    payload = {
        "personnel_id": p_a2.id,
        "checkin_date": str(date.today()),
        "sleep_hours": 7.0,
        "sleep_quality": 3,
        "mood_score": 3,
        "energy_score": 3,
        "workload_score": 3,
        "stress_score": 3
    }
    db.close()
    res = client.post(f"{settings.API_V1_STR}/wellness/checkins", json=payload, headers=headers)
    assert res.status_code == 422

def test_attack_spoof_personnel_id_in_support_rejected(setup_security_db):
    token = get_token("pa1_s@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_a2 = db.query(User).filter(User.email == "pa2_s@example.com").first()

    payload = {
        "personnel_id": p_a2.id,
        "request_type": "WORKLOAD",
        "message": "Falsified support message."
    }
    db.close()
    res = client.post(f"{settings.API_V1_STR}/support/requests", json=payload, headers=headers)
    assert res.status_code == 422

def test_attack_commander_individual_privacy_breach_blocked(setup_security_db):
    token = get_token("ca_s@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_a1 = db.query(User).filter(User.email == "pa1_s@example.com").first()

    # 1. Commander attempts to read individual wellness
    res_well = client.get(f"{settings.API_V1_STR}/wellness/{p_a1.id}", headers=headers)
    assert res_well.status_code == 403

    # 2. Commander attempts to read support requests
    res_supp = client.get(f"{settings.API_V1_STR}/support/requests", headers=headers)
    assert res_supp.status_code == 403

    # 3. Commander attempts to read interventions
    res_intv = client.get(f"{settings.API_V1_STR}/interventions", headers=headers)
    assert res_intv.status_code == 403
    db.close()

def test_attack_admin_welfare_bypass_blocked(setup_security_db):
    token = get_token("adma_s@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_a1 = db.query(User).filter(User.email == "pa1_s@example.com").first()

    # Admin attempts to read individual wellness
    res = client.get(f"{settings.API_V1_STR}/wellness/{p_a1.id}", headers=headers)
    assert res.status_code == 403
    db.close()

def test_attack_cross_org_isolation_enforced(setup_security_db):
    token_w_a = get_token("wa_s@example.com")
    headers_w_a = {"Authorization": f"Bearer {token_w_a}"}
    db = TestingSessionLocal()
    p_b1 = db.query(User).filter(User.email == "pb1_s@example.com").first()

    # Welfare officer in Org A attempts to view personnel in Org B
    res_p = client.get(f"{settings.API_V1_STR}/personnel/{p_b1.id}", headers=headers_w_a)
    assert res_p.status_code == 404

    # Welfare officer in Org A attempts to view wellness of Org B personnel
    res_w = client.get(f"{settings.API_V1_STR}/wellness/{p_b1.id}", headers=headers_w_a)
    assert res_w.status_code == 404
    db.close()

def test_audit_logs_contain_no_sensitive_values(setup_security_db):
    db = TestingSessionLocal()
    logs = db.query(AuditLog).all()
    for log in logs:
        assert not hasattr(log, "message") or log.message is None
        assert not hasattr(log, "stress_score")
        assert not hasattr(log, "notes")
    db.close()
