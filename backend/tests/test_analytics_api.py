import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, WellnessCheckin, AuditLog
from app.models.enums import UserRole, UserStatus, AuditAction
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_analytics_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_ANALYTICS", name="Analytics Org")
    db.add(org)
    db.commit()

    unit_large = Unit(organization_id=org.id, unit_code="U_LARGE", unit_name="Large Unit")
    unit_small = Unit(organization_id=org.id, unit_code="U_SMALL", unit_name="Small Unit")
    db.add_all([unit_large, unit_small])
    db.commit()

    # Commander and Welfare Officer
    commander = User(
        organization_id=org.id,
        unit_id=None,
        user_code="CMD_AN",
        name="Analytics Commander",
        email="cmd_an@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    welfare = User(
        organization_id=org.id,
        unit_id=None,
        user_code="WLF_AN",
        name="Analytics Welfare",
        email="wlf_an@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    db.add_all([commander, welfare])
    db.commit()

    # Create 6 personnel in unit_large (meets cohort threshold of 5)
    large_users = []
    for i in range(6):
        u = User(
            organization_id=org.id,
            unit_id=unit_large.id,
            user_code=f"P_LG_{i}",
            name=f"Large Personnel {i}",
            email=f"p_lg_{i}@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        db.add(u)
        large_users.append(u)
    db.commit()

    # Create 2 personnel in unit_small (below cohort threshold of 5)
    small_users = []
    for i in range(2):
        u = User(
            organization_id=org.id,
            unit_id=unit_small.id,
            user_code=f"P_SM_{i}",
            name=f"Small Personnel {i}",
            email=f"p_sm_{i}@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        db.add(u)
        small_users.append(u)
    db.commit()

    # Add checkins for large unit users (across last 5 days)
    today = date.today()
    for u in large_users:
        for day_offset in range(3):
            c = WellnessCheckin(
                personnel_id=u.id,
                checkin_date=today - timedelta(days=day_offset),
                sleep_hours=7.0 + (day_offset * 0.5),
                sleep_quality=4,
                mood_score=4,
                energy_score=3,
                workload_score=3,
                stress_score=2
            )
            db.add(c)

    # Add checkins for small unit users
    for u in small_users:
        c = WellnessCheckin(
            personnel_id=u.id,
            checkin_date=today,
            sleep_hours=6.0,
            sleep_quality=3,
            mood_score=3,
            energy_score=2,
            workload_score=4,
            stress_score=4
        )
        db.add(c)
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_commander_wellness_analytics_success(setup_analytics_db):
    token = get_token("cmd_an@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_cohort"] is False
    assert data["active_personnel_count"] == 8  # 6 large + 2 small
    assert data["summary"] is not None
    assert data["summary"]["average_sleep_hours"] > 0
    assert len(data["trend"]) > 0

def test_cohort_size_rule_for_small_unit(setup_analytics_db):
    token = get_token("cmd_an@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    unit_small = db.query(Unit).filter(Unit.unit_code == "U_SMALL").first()
    db.close()

    # Query specifically for unit_small (only 2 active personnel < 5)
    res = client.get(f"{settings.API_V1_STR}/analytics/wellness?unit_id={unit_small.id}", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_cohort"] is True
    assert data["active_personnel_count"] == 2
    assert data["summary"] is None
    assert data["trend"] == []
    assert "Cohort size too small" in data["message"]

def test_workload_analytics(setup_analytics_db):
    token = get_token("cmd_an@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/analytics/workload", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["insufficient_cohort"] is False
    assert data["summary"]["average_workload_score"] > 0
    assert len(data["trend"]) > 0

def test_unit_level_analytics_cohort_rules(setup_analytics_db):
    token = get_token("cmd_an@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/analytics/units", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "units" in data
    units = {u["unit_name"]: u for u in data["units"]}

    # Large unit has 6 personnel >= 5 -> statistics present
    assert units["Large Unit"]["insufficient_cohort"] is False
    assert units["Large Unit"]["participating_personnel_count"] == 6
    assert units["Large Unit"]["average_sleep_hours"] is not None

    # Small unit has 2 personnel < 5 -> statistics omitted
    assert units["Small Unit"]["insufficient_cohort"] is True
    assert units["Small Unit"]["participating_personnel_count"] == 2
    assert units["Small Unit"]["average_sleep_hours"] is None

def test_invalid_date_range_rejected(setup_analytics_db):
    token = get_token("cmd_an@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(
        f"{settings.API_V1_STR}/analytics/wellness?start_date=2026-09-10&end_date=2026-09-01",
        headers=headers
    )
    assert res.status_code == 422
