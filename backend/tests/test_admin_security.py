import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.models import User, Organization
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_security_db():
    db = TestingSessionLocal()
    org = Organization(organization_code="ORG_SEC", name="Sec Org")
    db.add(org)
    db.commit()
    db.refresh(org)

    admin = User(
        organization_id=org.id,
        user_code="ADM_SEC",
        email="admin_sec@example.com",
        name="Admin",
        password_hash=get_password_hash("password123"),
        role=UserRole.ADMINISTRATOR,
        status=UserStatus.ACTIVE
    )
    personnel = User(
        organization_id=org.id,
        user_code="PER_SEC",
        email="per_sec@example.com",
        name="Personnel",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    welfare = User(
        organization_id=org.id,
        user_code="WEL_SEC",
        email="wel_sec@example.com",
        name="Welfare",
        password_hash=get_password_hash("password123"),
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    commander = User(
        organization_id=org.id,
        user_code="COM_SEC",
        email="com_sec@example.com",
        name="Commander",
        password_hash=get_password_hash("password123"),
        role=UserRole.COMMANDER,
        status=UserStatus.ACTIVE
    )
    db.add_all([admin, personnel, welfare, commander])
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_personnel_cannot_access_admin_endpoints(setup_security_db):
    token = get_token("per_sec@example.com")
    response = client.get(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_welfare_officer_cannot_access_admin_endpoints(setup_security_db):
    token = get_token("wel_sec@example.com")
    response = client.get(
        "/api/v1/admin/organization",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_commander_cannot_access_admin_endpoints(setup_security_db):
    token = get_token("com_sec@example.com")
    response = client.get(
        "/api/v1/admin/settings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_admin_cannot_change_own_role(setup_security_db):
    token = get_token("admin_sec@example.com")
    
    db = TestingSessionLocal()
    admin_user = db.query(User).filter(User.email == "admin_sec@example.com").first()
    db.close()

    response = client.patch(
        f"/api/v1/admin/users/{admin_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": "PERSONNEL"}
    )
    assert response.status_code == 400
    assert "Cannot change your own role" in response.json()["detail"]

def test_admin_audit_logs_do_not_contain_sensitive_info(setup_security_db):
    token = get_token("admin_sec@example.com")
    response = client.get(
        "/api/v1/admin/audit-logs",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    if data["items"]:
        first_item = data["items"][0]
        assert "password" not in first_item
        assert "wellness_score" not in first_item
        assert "support_message" not in first_item
