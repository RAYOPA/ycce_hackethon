import pytest
from datetime import date, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, WellnessCheckin, SupportRequest, Intervention
from app.models.enums import (
    UserRole,
    UserStatus,
    SupportRequestType,
    SupportRequestStatus,
    InterventionActionType,
    InterventionStatus
)
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_report_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_REPORT", name="Report Org")
    db.add(org)
    db.commit()

    unit_lg = Unit(organization_id=org.id, unit_code="U_REP_LG", unit_name="Report Large Unit")
    unit_sm = Unit(organization_id=org.id, unit_code="U_REP_SM", unit_name="Report Small Unit")
    db.add_all([unit_lg, unit_sm])
    db.commit()

    commander = User(
        organization_id=org.id,
        unit_id=None,
        user_code="CMD_REP",
        name="Report Commander",
        email="cmd_rep@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    welfare = User(
        organization_id=org.id,
        unit_id=None,
        user_code="WLF_REP",
        name="Report Welfare",
        email="wlf_rep@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    db.add_all([commander, welfare])
    db.commit()

    # 6 personnel in large unit
    lg_users = []
    for i in range(6):
        u = User(
            organization_id=org.id,
            unit_id=unit_lg.id,
            user_code=f"P_REP_LG_{i}",
            name=f"Rep Large Personnel {i}",
            email=f"p_rep_lg_{i}@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        db.add(u)
        lg_users.append(u)
    db.commit()

    # 2 personnel in small unit
    sm_users = []
    for i in range(2):
        u = User(
            organization_id=org.id,
            unit_id=unit_sm.id,
            user_code=f"P_REP_SM_{i}",
            name=f"Rep Small Personnel {i}",
            email=f"p_rep_sm_{i}@example.com",
            password_hash=get_password_hash("password123"),
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        db.add(u)
        sm_users.append(u)
    db.commit()

    # Add checkins
    today = date.today()
    for u in lg_users:
        for offset in range(3):
            db.add(WellnessCheckin(
                personnel_id=u.id,
                checkin_date=today - timedelta(days=offset),
                sleep_hours=7.5,
                sleep_quality=4,
                mood_score=4,
                energy_score=3,
                workload_score=3,
                stress_score=2
            ))
    for u in sm_users:
        db.add(WellnessCheckin(
            personnel_id=u.id,
            checkin_date=today,
            sleep_hours=6.0,
            sleep_quality=3,
            mood_score=3,
            energy_score=2,
            workload_score=4,
            stress_score=4
        ))
    db.commit()

    # Add Support Requests
    db.add(SupportRequest(
        personnel_id=lg_users[0].id,
        request_type=SupportRequestType.GENERAL_WELLBEING,
        message="Confidential support message 1",
        status=SupportRequestStatus.OPEN
    ))
    db.add(SupportRequest(
        personnel_id=lg_users[1].id,
        request_type=SupportRequestType.WORKLOAD,
        message="Confidential support message 2",
        status=SupportRequestStatus.RESOLVED
    ))

    # Add Interventions
    db.add(Intervention(
        personnel_id=lg_users[0].id,
        assigned_officer_id=welfare.id,
        action_type=InterventionActionType.WELLNESS_FOLLOWUP,
        notes="Confidential officer notes 1",
        follow_up_date=today - timedelta(days=1),  # overdue/due
        status=InterventionStatus.IN_PROGRESS
    ))
    db.add(Intervention(
        personnel_id=lg_users[1].id,
        assigned_officer_id=welfare.id,
        action_type=InterventionActionType.RECOVERY_SUPPORT,
        notes="Confidential officer notes 2",
        follow_up_date=today,
        status=InterventionStatus.COMPLETED
    ))
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_commander_wellness_report(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/reports/wellness", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["report_version"] == "1.0"
    assert data["report_type"] == "WELLNESS_REPORT"
    assert data["insufficient_cohort"] is False
    assert data["summary"]["average_sleep_hours"] > 0
    assert len(data["trend"]) > 0

def test_commander_workload_report(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/reports/workload", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "WORKLOAD_REPORT"
    assert data["insufficient_cohort"] is False
    assert data["summary"]["average_workload_score"] > 0

def test_commander_unit_report(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/reports/units", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "UNIT_REPORT"
    units = {u["unit_name"]: u for u in data["units"]}
    assert units["Report Large Unit"]["insufficient_cohort"] is False
    assert units["Report Small Unit"]["insufficient_cohort"] is True

def test_welfare_activity_report(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/reports/welfare-activity", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "WELFARE_ACTIVITY_REPORT"
    summary = data["summary"]
    assert summary["support_requests_received"] == 2
    assert summary["open_requests"] == 1
    assert summary["resolved_requests"] == 1
    assert summary["interventions_created"] == 2
    assert summary["interventions_completed"] == 1
    assert summary["followups_due"] == 1
    assert summary["followups_completed"] == 1

def test_csv_exports_valid(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Wellness CSV
    res_w = client.get(f"{settings.API_V1_STR}/reports/wellness/export?format=csv", headers=headers)
    assert res_w.status_code == 200
    assert "text/csv" in res_w.headers["content-type"]
    assert "average_sleep_hours" in res_w.text
    assert "Confidential" not in res_w.text

    # 2. Workload CSV
    res_wl = client.get(f"{settings.API_V1_STR}/reports/workload/export?format=csv", headers=headers)
    assert res_wl.status_code == 200
    assert "text/csv" in res_wl.headers["content-type"]
    assert "average_workload_score" in res_wl.text

    # 3. Units CSV
    res_u = client.get(f"{settings.API_V1_STR}/reports/units/export?format=csv", headers=headers)
    assert res_u.status_code == 200
    assert "text/csv" in res_u.headers["content-type"]
    assert "Report Large Unit" in res_u.text
    assert "INSUFFICIENT_COHORT" in res_u.text

    # 4. Welfare Activity CSV
    res_act = client.get(f"{settings.API_V1_STR}/reports/welfare-activity/export?format=csv", headers=headers)
    assert res_act.status_code == 200
    assert "text/csv" in res_act.headers["content-type"]
    assert "support_requests_received,2" in res_act.text
    assert "Confidential" not in res_act.text

def test_json_exports_valid(setup_report_db):
    token = get_token("cmd_rep@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get(f"{settings.API_V1_STR}/reports/wellness/export?format=json", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["report_type"] == "WELLNESS_REPORT"
    assert data["summary"]["average_sleep_hours"] > 0
