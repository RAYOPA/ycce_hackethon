from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime
from app.models.enums import InterventionActionType, InterventionStatus

class InterventionCreate(BaseModel):
    personnel_id: str
    action_type: InterventionActionType
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    assigned_officer_id: Optional[str] = None

    model_config = ConfigDict(extra="forbid")

class InterventionSummary(BaseModel):
    id: str
    personnel_id: str
    assigned_officer_id: str
    action_type: InterventionActionType
    status: InterventionStatus
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterventionResponse(BaseModel):
    id: str
    personnel_id: str
    assigned_officer_id: str
    action_type: InterventionActionType
    notes: Optional[str] = None
    status: InterventionStatus
    follow_up_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InterventionUpdate(BaseModel):
    action_type: Optional[InterventionActionType] = None
    notes: Optional[str] = None
    follow_up_date: Optional[datetime] = None
    assigned_officer_id: Optional[str] = None
    status: Optional[InterventionStatus] = None

    model_config = ConfigDict(extra="forbid")

class InterventionReschedule(BaseModel):
    follow_up_date: datetime

    model_config = ConfigDict(extra="forbid")

class InterventionListResponse(BaseModel):
    items: List[InterventionSummary]
    page: int
    page_size: int
    total: int
