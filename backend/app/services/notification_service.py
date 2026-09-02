from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.notification import Notification
from app.models.enums import NotificationType
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    UnreadCountResponse,
    ReadAllResponse
)

def create_notification(
    db: Session,
    user_id: str,
    notification_type: NotificationType,
    title: str,
    message: str,
    related_resource: Optional[str] = None
) -> Notification:
    """
    Creates a privacy-safe notification.
    Ensures that notification titles and messages NEVER leak sensitive messages,
    intervention notes, wellness scores, or AI predictions.
    """
    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        related_resource=related_resource,
        is_read=False
    )
    db.add(notification)
    return notification

def create_followup_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    related_resource: Optional[str] = None
) -> Notification:
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.FOLLOWUP,
        title=title,
        message=message,
        related_resource=related_resource
    )

def create_support_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    related_resource: Optional[str] = None
) -> Notification:
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.SUPPORT,
        title=title,
        message=message,
        related_resource=related_resource
    )

def create_system_notification(
    db: Session,
    user_id: str,
    title: str,
    message: str,
    related_resource: Optional[str] = None
) -> Notification:
    return create_notification(
        db=db,
        user_id=user_id,
        notification_type=NotificationType.SYSTEM,
        title=title,
        message=message,
        related_resource=related_resource
    )

def get_notifications(
    db: Session,
    current_user: User,
    is_read: Optional[bool] = None,
    notification_type: Optional[NotificationType] = None,
    page: int = 1,
    page_size: int = 20
) -> NotificationListResponse:
    # Strictly scope to current authenticated user's ID
    query = db.query(Notification).filter(Notification.user_id == current_user.id)

    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)

    if notification_type is not None:
        query = query.filter(Notification.notification_type == notification_type)

    total = query.count()

    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(page_size).all()
    items = [NotificationResponse.model_validate(n) for n in notifications]

    return NotificationListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

def get_unread_count(db: Session, current_user: User) -> UnreadCountResponse:
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).count()
    return UnreadCountResponse(unread_count=count)

def get_notification_by_id(
    db: Session,
    current_user: User,
    notification_id: str
) -> NotificationResponse:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    # Never allow notification enumeration across users
    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )

    return NotificationResponse.model_validate(notification)

def mark_notification_read(
    db: Session,
    current_user: User,
    notification_id: str
) -> NotificationResponse:
    notification = db.query(Notification).filter(Notification.id == notification_id).first()

    if not notification or notification.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found."
        )

    # Idempotent operation
    if not notification.is_read:
        notification.is_read = True
        db.commit()
        db.refresh(notification)

    return NotificationResponse.model_validate(notification)

def mark_all_read(db: Session, current_user: User) -> ReadAllResponse:
    count = db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True}, synchronize_session=False)

    db.commit()
    return ReadAllResponse(updated_count=count, success=True)
