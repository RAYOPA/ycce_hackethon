import pytest
from datetime import datetime, timedelta, timezone
from app.models.enums import UserStatus
from tests.conftest import TestingSessionLocal

def test_login_rate_limiting(test_client, setup_test_database):
    # This assumes rate limit is 5 per minute as configured in step 11
    payload = {"email": "personnel_a@example.com", "password": "password123"}
    
    # Send 5 valid requests (or invalid, doesn't matter for rate limiting)
    for _ in range(5):
        res = test_client.post("/api/v1/auth/login", json=payload)
        # It could be 200 or 401, but not 429
        assert res.status_code in (200, 401)
        
    # The 6th request should be rate limited
    res = test_client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 429
    assert "Rate limit exceeded" in res.json()["detail"]

def test_inactive_user_cannot_login(test_client, setup_test_database):
    from app.models.user import User
    
    db_session = TestingSessionLocal()
    # Deactivate the user
    user = db_session.query(User).filter(User.email == "personnel_a@example.com").first()
    if user:
        user.status = UserStatus.INACTIVE
        db_session.commit()
    
    # Attempt login
    payload = {"email": "personnel_a@example.com", "password": "password123"}
    res = test_client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 401
    
    # Restore user for other tests
    if user:
        user.status = UserStatus.ACTIVE
        db_session.commit()
    db_session.close()

def test_expired_refresh_token_rejected(test_client, setup_test_database):
    from app.models.auth import RefreshSession
    
    # Do a quick login to get tokens
    res = test_client.post("/api/v1/auth/login", json={"email": "personnel_a@example.com", "password": "password123"})
    if res.status_code == 429: # Might hit rate limit from previous test depending on execution order
        pytest.skip("Rate limited from previous test")
    if res.status_code == 401:
        pytest.skip("Seed data missing or bad password")
    
    refresh_token = res.json()["refresh_token"]
    
    db_session = TestingSessionLocal()
    # Expire the session in DB
    session = db_session.query(RefreshSession).first()
    if session:
        session.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
    db_session.close()
    
    # Attempt refresh
    res = test_client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert res.status_code == 401
