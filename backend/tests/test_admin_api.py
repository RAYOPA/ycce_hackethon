import pytest
from fastapi.testclient import TestClient
from datetime import date

from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal
from app.models.settings import OrganizationSettings

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_admin_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_ADMIN", name="Admin Org")
    db.add(org)
    db.commit()
    db.refresh(org)
    
    org_settings = OrganizationSettings(
        organization_id=org.id,
        checkin_frequency="DAILY",
        minimum_analytics_cohort_size=5,
        timezone="UTC",
        notifications_enabled=True
    )
    db.add(org_settings)
    db.commit()

    unit_a = Unit(organization_id=org.id, unit_code="UA", unit_name="Unit A")
    db.add(unit_a)
    db.commit()

    # Administrator
    admin = User(
        organization_id=org.id,
        unit_id=None,
        user_code="ADM_01",
        name="Admin",
        email="admin@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMINISTRATOR,
        status=UserStatus.ACTIVE
    )
    db.add(admin)
    db.commit()
    
    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_admin_get_organization(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.get(
        "/api/v1/admin/organization",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Admin Org"

def test_admin_update_organization(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.patch(
        "/api/v1/admin/organization",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Admin Org"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Admin Org"

def test_admin_create_unit(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.post(
        "/api/v1/admin/units",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "unit_code": "TEST_UNIT",
            "unit_name": "Test Unit Name"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["unit_code"] == "TEST_UNIT"

def test_admin_create_user(setup_admin_db):
    token = get_token("admin@example.com")
    
    db = TestingSessionLocal()
    unit = db.query(Unit).filter(Unit.unit_code == "UA").first()
    db.close()
    
    response = client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "user_code": "NEW_USER_001",
            "email": "newuser@test.com",
            "name": "New User",
            "password": "securepassword",
            "role": "PERSONNEL",
            "unit_id": unit.id
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["role"] == "PERSONNEL"
    assert "password_hash" not in data

def test_admin_list_users(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 1

def test_admin_get_settings(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.get(
        "/api/v1/admin/settings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "checkin_frequency" in data

def test_admin_update_settings(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.patch(
        "/api/v1/admin/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"minimum_analytics_cohort_size": 10}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["minimum_analytics_cohort_size"] == 10

def test_admin_audit_logs(setup_admin_db):
    token = get_token("admin@example.com")
    response = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
