from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(from_attributes=True)
