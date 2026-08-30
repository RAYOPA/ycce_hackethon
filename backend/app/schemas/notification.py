from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: str
    notification_type: str
    title: str
    message: str
    is_read: bool
    related_resource: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
