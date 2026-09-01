from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class SupportRequestBase(BaseModel):
    request_type: str
    message: Optional[str] = None

class SupportRequestCreate(SupportRequestBase):
    pass

class SupportRequestResponse(SupportRequestBase):
    id: str
    personnel_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
