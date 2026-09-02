from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.enums import ProcessingPurpose, ConsentStatus

class GovernancePolicyBase(BaseModel):
    allowed_purposes: List[ProcessingPurpose]
    is_active: bool = True

class GovernancePolicyUpdate(GovernancePolicyBase):
    pass

class GovernancePolicyResponse(GovernancePolicyBase):
    id: str
    organization_id: str
    version: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserConsentUpdate(BaseModel):
    purpose: ProcessingPurpose
    status: ConsentStatus

class UserConsentResponse(BaseModel):
    id: str
    user_id: str
    purpose: ProcessingPurpose
    status: ConsentStatus
    policy_version: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
