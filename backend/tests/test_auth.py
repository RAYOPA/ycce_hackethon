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
def setup_auth_db():
    db = TestingSessionLocal()
    
    org = Organization(organization_code="AUTH_ORG", name="Auth Test Org")
    db.add(org)
    db.commit()
    
    unit = Unit(organization_id=org.id, unit_code="AUTH_UNIT", unit_name="Auth Unit")
    db.add(unit)
    db.commit()
    
    active_user = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="AUTH_01",
        name="Active Auth User",
        email="active@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    
    inactive_user = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="AUTH_02",
        name="Inactive Auth User",
        email="inactive@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.INACTIVE
    )
    
    db.add_all([active_user, inactive_user])
    db.commit()
    
    yield db
    db.close()

def test_login_success(setup_auth_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "active@example.com"

def test_login_wrong_password(setup_auth_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_inactive_user(setup_auth_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "inactive@example.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_refresh_token(setup_auth_db):
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token

def test_refresh_token_invalid(setup_auth_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": "invalid_or_fake_token"}
    )
    assert response.status_code == 401

def test_logout(setup_auth_db):
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]
    
    logout_resp = client.post(
        f"{settings.API_V1_STR}/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_resp.status_code == 200
    
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 401

def test_get_current_user_me(setup_auth_db):
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "active@example.com"
    assert data["role"] == "PERSONNEL"
