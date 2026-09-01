from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class InterventionBase(BaseModel):
    personnel_id: str
    action_type: str
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None

class InterventionCreate(InterventionBase):
    pass

class InterventionUpdate(BaseModel):
    notes: Optional[str] = None
    status: Optional[str] = None

class InterventionResponse(InterventionBase):
    id: str
    assigned_officer_id: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
