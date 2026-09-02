import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus, CheckinFrequency
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_wellness_db():
    db = TestingSessionLocal()

    org_daily = Organization(organization_code="ORG_W_DAILY", name="Daily Org", wellness_checkin_frequency=CheckinFrequency.DAILY)
    org_flex = Organization(organization_code="ORG_W_FLEX", name="Flex Org", wellness_checkin_frequency=CheckinFrequency.FLEXIBLE)
    db.add_all([org_daily, org_flex])
    db.commit()

    unit1 = Unit(organization_id=org_daily.id, unit_code="U_W_DAILY", unit_name="Unit Daily")
    unit_flex = Unit(organization_id=org_flex.id, unit_code="U_W_FLEX", unit_name="Unit Flex")
    db.add_all([unit1, unit_flex])
    db.commit()

    p_daily = User(
        organization_id=org_daily.id,
        unit_id=unit1.id,
        user_code="P_W_DAILY",
        name="Daily Personnel",
        email="pdaily_w@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    p_flex = User(
        organization_id=org_flex.id,
        unit_id=unit_flex.id,
        user_code="P_W_FLEX",
        name="Flex Personnel",
        email="pflex_w@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    w_daily = User(
        organization_id=org_daily.id,
        unit_id=unit1.id,
        user_code="W_W_DAILY",
        name="Daily Welfare Officer",
        email="wdaily_w@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    c_daily = User(
        organization_id=org_daily.id,
        unit_id=unit1.id,
        user_code="C_W_DAILY",
        name="Daily Commander",
        email="cdaily_w@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    db.add_all([p_daily, p_flex, w_daily, c_daily])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_record_wellness_checkin_success(setup_wellness_db):
    token = get_token("pdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "checkin_date": str(date.today()),
        "sleep_hours": 7.5,
        "sleep_quality": 4,
        "mood_score": 4,
        "energy_score": 3,
        "workload_score": 3,
        "stress_score": 2
    }
    res = client.post(f"{settings.API_V1_STR}/wellness/checkins", json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "recorded"
    assert "id" in data

def test_daily_policy_duplicate_rejected(setup_wellness_db):
    token = get_token("pdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "checkin_date": str(date.today()),
        "sleep_hours": 6.0,
        "sleep_quality": 3,
        "mood_score": 3,
        "energy_score": 3,
        "workload_score": 4,
        "stress_score": 4
    }
    res = client.post(f"{settings.API_V1_STR}/wellness/checkins", json=payload, headers=headers)
    assert res.status_code == 409
    assert "already been recorded" in res.json()["detail"]

def test_flexible_policy_allows_multiple(setup_wellness_db):
    token = get_token("pflex_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    payload1 = {
        "checkin_date": str(date.today()),
        "sleep_hours": 8.0,
        "sleep_quality": 5,
        "mood_score": 5,
        "energy_score": 5,
        "workload_score": 2,
        "stress_score": 1
    }
    res1 = client.post(f"{settings.API_V1_STR}/wellness/checkins", json=payload1, headers=headers)
    assert res1.status_code == 201

    payload2 = {
        "checkin_date": str(date.today() - timedelta(days=1)),
        "sleep_hours": 7.0,
        "sleep_quality": 4,
        "mood_score": 4,
        "energy_score": 4,
        "workload_score": 3,
        "stress_score": 2
    }
    res2 = client.post(f"{settings.API_V1_STR}/wellness/checkins", json=payload2, headers=headers)
    assert res2.status_code == 201

def test_get_my_wellness_history(setup_wellness_db):
    token = get_token("pdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(f"{settings.API_V1_STR}/wellness/me", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 1
    assert data["items"][0]["sleep_hours"] == 7.5

def test_invalid_date_range_rejected(setup_wellness_db):
    token = get_token("pdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    res = client.get(
        f"{settings.API_V1_STR}/wellness/me?start_date=2026-09-10&end_date=2026-09-01",
        headers=headers
    )
    assert res.status_code == 422

def test_commander_forbidden_from_individual_wellness(setup_wellness_db):
    token = get_token("cdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_daily = db.query(User).filter(User.email == "pdaily_w@example.com").first()
    res = client.get(f"{settings.API_V1_STR}/wellness/{p_daily.id}", headers=headers)
    db.close()
    assert res.status_code == 403

def test_welfare_officer_can_view_individual_wellness(setup_wellness_db):
    token = get_token("wdaily_w@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    db = TestingSessionLocal()
    p_daily = db.query(User).filter(User.email == "pdaily_w@example.com").first()
    res = client.get(f"{settings.API_V1_STR}/wellness/{p_daily.id}", headers=headers)
    db.close()
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 1
