from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import NotificationType
from app.api.deps import get_current_user
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    ReadAllResponse
)
from app.services.notification_service import (
    get_notifications,
    get_unread_count,
    get_notification_by_id,
    mark_notification_read,
    mark_all_read,
    create_notification
)

router = APIRouter()

@router.get("", response_model=NotificationListResponse, summary="Get Current User's Notifications")
def list_user_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status (true/false)"),
    notification_type: Optional[str] = Query(None, description="Filter by notification type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Normalize enum
    parsed_type = None
    if notification_type:
        ntype = notification_type.upper().replace("_REQUEST", "").replace("_ALERT", "").replace("_", "")
        # Try to map it to the actual enum
        for t in NotificationType:
            if t.value == ntype:
                parsed_type = t
                break

    return get_notifications(
        db=db,
        current_user=current_user,
        is_read=is_read,
        notification_type=parsed_type,
        page=page,
        page_size=page_size
    )

@router.get("/unread-count", response_model=UnreadCountResponse, summary="Get Unread Notification Count")
def get_user_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_unread_count(db=db, current_user=current_user)

@router.patch("/read-all", response_model=ReadAllResponse, summary="Mark All Notifications as Read")
@router.put("/read-all", response_model=ReadAllResponse, summary="Mark All Notifications as Read", include_in_schema=False)
def mark_all_user_notifications_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_all_read(db=db, current_user=current_user)

@router.get("/{notification_id}", response_model=NotificationResponse, summary="Get Notification by ID")
def get_single_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_notification_by_id(
        db=db,
        current_user=current_user,
        notification_id=notification_id
    )

@router.patch("/{notification_id}/read", response_model=NotificationResponse, summary="Mark Single Notification as Read")
@router.put("/{notification_id}/read", response_model=NotificationResponse, summary="Mark Single Notification as Read", include_in_schema=False)
def mark_single_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_notification_read(
        db=db,
        current_user=current_user,
        notification_id=notification_id
    )

from app.schemas.notification import NotificationTestCreate

@router.post("/test", response_model=NotificationResponse, summary="Send Test Notification")
def send_test_notification(
    test_in: NotificationTestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_notification(
        db=db,
        user_id=current_user.id,
        notification_type=test_in.notification_type or NotificationType.SYSTEM,
        title=test_in.title,
        message=test_in.message
    )
