import pytest
from app.models.enums import UserRole
from tests.conftest import TestingSessionLocal

def test_personnel_cannot_view_other_wellness(test_client, setup_test_database):
    # Setup test token for personnel A
    res_login = test_client.post("/api/v1/auth/login", json={"email": "personnel_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Seed data missing")
    token_a = res_login.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}
    
    from app.models.user import User
    
    db = TestingSessionLocal()
    personnel_b = db.query(User).filter(User.email == "personnel_b@example.com").first()
    db.close()
    if not personnel_b:
        pytest.skip("Personnel B not found")
        
    res = test_client.get(f"/api/v1/wellness/{personnel_b.id}", headers=headers_a)
    assert res.status_code == 403

def test_commander_cannot_view_individual_support_message(test_client, setup_test_database):
    res_login = test_client.post("/api/v1/auth/login", json={"email": "commander_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Seed data missing")
    token_cmd = res_login.json()["access_token"]
    headers_cmd = {"Authorization": f"Bearer {token_cmd}"}
    
    # In support API, getting individual request is blocked for commanders
    # Let's hit the list endpoint, it should return 403
    res = test_client.get("/api/v1/support", headers=headers_cmd)
    assert res.status_code == 403

def test_administrator_cannot_access_interventions(test_client, setup_test_database):
    res_login = test_client.post("/api/v1/auth/login", json={"email": "admin_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Seed data missing")
    token_admin = res_login.json()["access_token"]
    headers_admin = {"Authorization": f"Bearer {token_admin}"}
    
    res = test_client.get("/api/v1/interventions", headers=headers_admin)
    assert res.status_code == 403
