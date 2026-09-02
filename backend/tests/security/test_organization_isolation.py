import pytest
import uuid
from app.models.organization import Organization
from app.models.user import User
from app.models.enums import UserRole
from tests.conftest import TestingSessionLocal

def test_cross_organization_access_blocked(test_client, setup_test_database):
    db_session = TestingSessionLocal()
    # Create a second organization and an admin in it
    org_2_id = str(uuid.uuid4())
    org_2 = Organization(id=org_2_id, organization_code="ORG-2", name="Second Org")
    db_session.add(org_2)
    
    admin_2_id = str(uuid.uuid4())
    admin_2 = User(
        email="admin2@org2.com",
        name="Admin 2",
        user_code="A2",
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$R5vKqY7KqY7KqY7KqY7KqQ$qY7KqY7KqY7KqY7KqY7KqY7KqY7KqY7KqY7KqY7KqY7",
        role=UserRole.ADMINISTRATOR,
        organization_id=org_2_id,
        status="ACTIVE"
    )
    db_session.add(admin_2)
    db_session.commit()
    db_session.close()
    
    # Let's hit the admin users endpoint with Admin 1's token and try to edit Admin 2
    res_login = test_client.post("/api/v1/auth/login", json={"email": "admin_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Login failed, seed data missing")
    token_1 = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token_1}"}
    
    res = test_client.patch(f"/api/v1/admin/users/{admin_2_id}/status", headers=headers, json={"status": "INACTIVE"})
    
    # Admin 1 should get a 404 because OrganizationScope filters out users from other orgs
    assert res.status_code == 404
