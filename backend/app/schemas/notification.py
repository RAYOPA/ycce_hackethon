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

from pydantic import BaseModel, ConfigDict, Field, model_validator

class UnreadCountResponse(BaseModel):
    unread_count: int
    count: Optional[int] = None

    @model_validator(mode="after")
    def sync_count(self):
        if self.count is None:
            self.count = self.unread_count
        return self

class ReadAllResponse(BaseModel):
    updated_count: int
    success: bool = True

class NotificationTestCreate(BaseModel):
    title: str = Field(..., max_length=100)
    message: str = Field(..., max_length=500)
    notification_type: Optional[NotificationType] = NotificationType.SYSTEM
