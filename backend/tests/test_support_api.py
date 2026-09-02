import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, Notification
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_support_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_SUPP_MOD", name="Support Org")
    db.add(org)
    db.commit()

    unit = Unit(organization_id=org.id, unit_code="U_SUPP_MOD", unit_name="Unit Supp")
    db.add(unit)
    db.commit()

    p1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="P_SUPP_M1",
        name="Support Personnel One",
        email="psupp1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    p2 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="P_SUPP_M2",
        name="Support Personnel Two",
        email="psupp2_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="W_SUPP_M1",
        name="Support Officer One",
        email="wsupp1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    c1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="C_SUPP_M1",
        name="Support Commander One",
        email="csupp1_m@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    db.add_all([p1, p2, w1, c1])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_personnel_create_support_request(setup_support_db):
    token = get_token("psupp1_m@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "request_type": "GENERAL_WELLBEING",
        "message": "I would like to discuss some personal challenges."
    }
    res = client.post(f"{settings.API_V1_STR}/support/requests", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "OPEN"
    assert "id" in data

    # Verify notification created for welfare officer
    db = TestingSessionLocal()
    w1 = db.query(User).filter(User.email == "wsupp1_m@example.com").first()
    notifs = db.query(Notification).filter(Notification.user_id == w1.id).all()
    db.close()
    assert len(notifs) >= 1
    assert "personal challenges" not in notifs[0].message

def test_empty_message_rejected(setup_support_db):
    token = get_token("psupp1_m@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "request_type": "WORKLOAD",
        "message": "    "
    }
    res = client.post(f"{settings.API_V1_STR}/support/requests", json=payload, headers=headers)
    assert res.status_code == 422

def test_personnel_list_own_support_requests(setup_support_db):
    token = get_token("psupp1_m@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{settings.API_V1_STR}/support/requests", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 1

def test_welfare_officer_view_queue_and_update_status(setup_support_db):
    token_w = get_token("wsupp1_m@example.com")
    headers_w = {"Authorization": f"Bearer {token_w}"}

    # Queue list does not contain private message
    res_list = client.get(f"{settings.API_V1_STR}/support/requests", headers=headers_w)
    assert res_list.status_code == 200
    items = res_list.json()["items"]
    assert len(items) >= 1
    req_id = items[0]["id"]
    assert "message" not in items[0]

    # Officer can view full request details with message
    res_single = client.get(f"{settings.API_V1_STR}/support/requests/{req_id}", headers=headers_w)
    assert res_single.status_code == 200
    assert res_single.json()["message"] == "I would like to discuss some personal challenges."

    # Update status OPEN -> IN_REVIEW
    res_patch = client.patch(
        f"{settings.API_V1_STR}/support/requests/{req_id}",
        json={"status": "IN_REVIEW"},
        headers=headers_w
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "IN_REVIEW"

    # Invalid transition (IN_REVIEW -> OPEN is invalid)
    res_invalid = client.patch(
        f"{settings.API_V1_STR}/support/requests/{req_id}",
        json={"status": "OPEN"},
        headers=headers_w
    )
    assert res_invalid.status_code == 400

def test_commander_forbidden_from_support_requests(setup_support_db):
    token_c = get_token("csupp1_m@example.com")
    headers_c = {"Authorization": f"Bearer {token_c}"}
    res = client.get(f"{settings.API_V1_STR}/support/requests", headers=headers_c)
    assert res.status_code == 403
