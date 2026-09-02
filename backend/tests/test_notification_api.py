import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit, Notification
from app.models.enums import UserRole, UserStatus, NotificationType
from app.core.security import get_password_hash
from app.services.notification_service import create_notification, create_support_notification
from tests.conftest import TestingSessionLocal

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_notification_db():
    db = TestingSessionLocal()

    org = Organization(organization_code="ORG_NOTIF", name="Notification Org")
    db.add(org)
    db.commit()

    unit = Unit(organization_id=org.id, unit_code="U_NOTIF", unit_name="Unit Notif")
    db.add(unit)
    db.commit()

    u1 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="N_USR1",
        name="Notif User One",
        email="n_user1@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    u2 = User(
        organization_id=org.id,
        unit_id=unit.id,
        user_code="N_USR2",
        name="Notif User Two",
        email="n_user2@example.com",
        password_hash=get_password_hash("password123"),
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    db.add_all([u1, u2])
    db.commit()

    # Create notifications for u1
    create_support_notification(db, u1.id, "Support Update", "Your support request has been updated.", "req_01")
    create_notification(db, u1.id, NotificationType.SYSTEM, "System Maintenance", "Scheduled maintenance tonight.")
    create_notification(db, u1.id, NotificationType.FOLLOWUP, "Follow-up Scheduled", "Your follow-up is scheduled.")

    # Create notification for u2
    create_notification(db, u2.id, NotificationType.SYSTEM, "User 2 System Notice", "Notice for user 2.")
    db.commit()

    yield db
    db.close()

def get_token(email: str):
    res = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return res.json()["access_token"]

def test_user_can_view_own_notifications_and_unread_count(setup_notification_db):
    token = get_token("n_user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Unread count
    res_count = client.get(f"{settings.API_V1_STR}/notifications/unread-count", headers=headers)
    assert res_count.status_code == 200
    assert res_count.json()["unread_count"] == 3

    # 2. List notifications
    res_list = client.get(f"{settings.API_V1_STR}/notifications", headers=headers)
    assert res_list.status_code == 200
    data = res_list.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3
    # Check that u2's notification is NOT in u1's list
    titles = [item["title"] for item in data["items"]]
    assert "User 2 System Notice" not in titles

def test_notification_filtering(setup_notification_db):
    token = get_token("n_user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Filter by notification_type=SUPPORT
    res = client.get(f"{settings.API_V1_STR}/notifications?notification_type=SUPPORT", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["notification_type"] == "SUPPORT"

def test_mark_single_notification_read_idempotent(setup_notification_db):
    token = get_token("n_user1@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Get first notification
    res_list = client.get(f"{settings.API_V1_STR}/notifications", headers=headers)
    notif_id = res_list.json()["items"][0]["id"]

    # Mark as read
    res_read = client.patch(f"{settings.API_V1_STR}/notifications/{notif_id}/read", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["is_read"] is True

    # Mark again (idempotent test)
    res_read_again = client.patch(f"{settings.API_V1_STR}/notifications/{notif_id}/read", headers=headers)
    assert res_read_again.status_code == 200
    assert res_read_again.json()["is_read"] is True

    # Unread count should now be 2
    res_count = client.get(f"{settings.API_V1_STR}/notifications/unread-count", headers=headers)
    assert res_count.json()["unread_count"] == 2

def test_user_cannot_access_or_modify_other_user_notification(setup_notification_db):
    token1 = get_token("n_user1@example.com")
    token2 = get_token("n_user2@example.com")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Get u2's notification ID
    res_u2 = client.get(f"{settings.API_V1_STR}/notifications", headers=headers2)
    u2_notif_id = res_u2.json()["items"][0]["id"]

    # u1 tries to GET u2's notification -> 404 (No enumeration)
    res_get = client.get(f"{settings.API_V1_STR}/notifications/{u2_notif_id}", headers=headers1)
    assert res_get.status_code == 404

    # u1 tries to mark u2's notification as read -> 404
    res_patch = client.patch(f"{settings.API_V1_STR}/notifications/{u2_notif_id}/read", headers=headers1)
    assert res_patch.status_code == 404

def test_mark_all_read(setup_notification_db):
    token1 = get_token("n_user1@example.com")
    token2 = get_token("n_user2@example.com")
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # u1 marks all read
    res_read_all = client.patch(f"{settings.API_V1_STR}/notifications/read-all", headers=headers1)
    assert res_read_all.status_code == 200
    assert res_read_all.json()["updated_count"] == 2  # 2 remaining unread

    # u1 unread count is now 0
    res_count1 = client.get(f"{settings.API_V1_STR}/notifications/unread-count", headers=headers1)
    assert res_count1.json()["unread_count"] == 0

    # u2 unread count is still 1 (unaffected)
    res_count2 = client.get(f"{settings.API_V1_STR}/notifications/unread-count", headers=headers2)
    assert res_count2.json()["unread_count"] == 1
