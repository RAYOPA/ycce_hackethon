from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Optional
from datetime import datetime
from app.models.enums import SupportRequestType, SupportRequestStatus

class SupportRequestCreate(BaseModel):
    request_type: SupportRequestType
    message: str = Field(..., min_length=1, max_length=2000, description="Support request description")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Support request message cannot be blank")
        return trimmed

    model_config = ConfigDict(extra="forbid")

class SupportRequestCreatedResponse(BaseModel):
    id: str
    status: SupportRequestStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupportRequestSummary(BaseModel):
    id: str
    personnel_id: str
    personnel_code: Optional[str] = None
    unit_id: Optional[str] = None
    request_type: SupportRequestType
    status: SupportRequestStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupportRequestResponse(BaseModel):
    id: str
    personnel_id: str
    personnel_code: Optional[str] = None
    unit_id: Optional[str] = None
    request_type: SupportRequestType
    message: Optional[str] = None
    status: SupportRequestStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SupportRequestUpdate(BaseModel):
    status: SupportRequestStatus

    model_config = ConfigDict(extra="forbid")

class SupportRequestListResponse(BaseModel):
    items: List[SupportRequestSummary]
    page: int
    page_size: int
    total: int
