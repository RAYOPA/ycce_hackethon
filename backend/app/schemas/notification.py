from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.enums import NotificationType

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    is_read: bool
    related_resource: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    page: int
    page_size: int
    total: int

class UnreadCountResponse(BaseModel):
    unread_count: int

class ReadAllResponse(BaseModel):
    updated_count: int
    success: bool = True
