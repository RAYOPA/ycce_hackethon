import pytest

def test_pagination_limits(test_client, setup_test_database):
    res_login = test_client.post("/api/v1/auth/login", json={"email": "admin_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Seed data missing")
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Try an excessively large page_size
    res = test_client.get("/api/v1/admin/users?page_size=1000000", headers=headers)
    assert res.status_code == 422
    assert "Input should be less than or equal to 100" in res.text

def test_invalid_uuid(test_client, setup_test_database):
    res_login = test_client.post("/api/v1/auth/login", json={"email": "personnel_a@example.com", "password": "password123"})
    if res_login.status_code != 200:
        pytest.skip("Seed data missing")
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Send a malformed UUID to an endpoint that expects a valid one
    # Note: depends on path param typing, if typed as str it might return 404, if UUID it returns 422
    # In personnel.py, personnel_id is str, but in backend logic it might fail safely or return 404
    res = test_client.get("/api/v1/personnel/invalid-uuid-format", headers=headers)
    # Both are safe (no 500)
    assert res.status_code in (422, 404)
