import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from app.services.intervention_service import get_due_followups
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_intervention_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_INTV_M", name="Intervention Org")
    db.add(org)
    db.commit()

    unit = Unit(organization_id=org.id, unit_code="U_INTV_M", unit_name="Unit Intv")
    db.add(unit)
    db.commit()

    p1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="P_INTV_M1",
        name="Intervention Personnel One",
        email="pintv1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="W_INTV_M1",
        name="Intervention Welfare Officer One",
        email="wintv1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    c1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="C_INTV_M1",
        name="Intervention Commander One",
        email="cintv1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    db.add_all([p1, w1, c1])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_create_and_manage_intervention(setup_intervention_db):
    token_w = get_token("wintv1_m@example.com")
    headers_w = {"Authorization": f"Bearer {token_w}"}

    db = TestingSessionLocal()
    p1 = db.query(User).filter(User.email == "pintv1_m@example.com").first()

    follow_up = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()

    # 1. Create Intervention
    payload = {
        "personnel_id": p1.id,
        "action_type": "WELLNESS_FOLLOWUP",
        "notes": "Schedule routine check on workload balance.",
        "follow_up_date": follow_up
    }
    res_create = client.post(f"{settings.API_V1_STR}/interventions", json=payload, headers=headers_w)
    assert res_create.status_code == 201
    intv_data = res_create.json()
    intv_id = intv_data["id"]
    assert intv_data["status"] == "PENDING"
    assert intv_data["notes"] == "Schedule routine check on workload balance."

    # 2. Personnel view own intervention (notes should be hidden/None)
    token_p = get_token("pintv1_m@example.com")
    headers_p = {"Authorization": f"Bearer {token_p}"}
    res_p_view = client.get(f"{settings.API_V1_STR}/interventions/{intv_id}", headers=headers_p)
    assert res_p_view.status_code == 200
    assert res_p_view.json()["notes"] is None

    # 3. Reschedule Intervention
    new_date = (datetime.now(timezone.utc) + timedelta(days=7)).isoformat()
    res_resched = client.post(
        f"{settings.API_V1_STR}/interventions/{intv_id}/reschedule",
        json={"follow_up_date": new_date},
        headers=headers_w
    )
    assert res_resched.status_code == 200
    assert res_resched.json()["status"] == "rescheduled"

    # 4. Due follow-ups query
    org = db.query(Organization).filter(Organization.organization_code == "ORG_INTV_M").first()
    due_list = get_due_followups(db, organization_id=org.id, due_date=datetime.now(timezone.utc) + timedelta(days=10))
    assert len(due_list) >= 1
    db.close()

    # 5. Complete Intervention
    res_complete = client.post(f"{settings.API_V1_STR}/interventions/{intv_id}/complete", headers=headers_w)
    assert res_complete.status_code == 200
    assert res_complete.json()["status"] == "completed"

def test_commander_forbidden_from_interventions(setup_intervention_db):
    token_c = get_token("cintv1_m@example.com")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    res = client.get(f"{settings.API_V1_STR}/interventions", headers=headers_c)
    assert res.status_code == 403
