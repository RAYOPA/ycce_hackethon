import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.config import settings
from app.models import Base, User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from app.core.database import get_db

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # Create required parent records
    org = Organization(organization_code="AUTH_ORG", name="Auth Test Org")
    db.add(org)
    db.commit()
    
    unit = Unit(organization_id=org.id, unit_code="AUTH_UNIT", unit_name="Auth Unit")
    db.add(unit)
    db.commit()
    
    # Create test users
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
    Base.metadata.drop_all(bind=engine)

def test_login_success(setup_db):
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

def test_login_wrong_password(setup_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_login_inactive_user(setup_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "inactive@example.com", "password": "password123"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"

def test_refresh_token(setup_db):
    # First login to get a refresh token
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    refresh_token = login_resp.json()["refresh_token"]
    
    # Now refresh it
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["refresh_token"] != refresh_token  # Token should have rotated

def test_refresh_token_invalid(setup_db):
    response = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": "invalid_or_fake_token"}
    )
    assert response.status_code == 401

def test_logout(setup_db):
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    access_token = login_resp.json()["access_token"]
    refresh_token = login_resp.json()["refresh_token"]
    
    # Logout
    logout_resp = client.post(
        f"{settings.API_V1_STR}/auth/logout",
        json={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_resp.status_code == 200
    
    # Trying to refresh after logout should fail
    refresh_resp = client.post(
        f"{settings.API_V1_STR}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 401

def test_get_current_user_me(setup_db):
    # First login to get token
    login_resp = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": "active@example.com", "password": "password123"}
    )
    token = login_resp.json()["access_token"]
    
    # Use token to hit /me endpoint
    response = client.get(
        f"{settings.API_V1_STR}/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "active@example.com"
    assert data["role"] == "PERSONNEL"
