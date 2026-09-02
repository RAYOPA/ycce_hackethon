from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.enums import CheckinFrequency

class OrganizationSettingsBase(BaseModel):
    checkin_frequency: CheckinFrequency = Field(..., description="Frequency of wellness check-ins")
    minimum_analytics_cohort_size: int = Field(..., ge=1, description="Minimum personnel required to show analytics")
    timezone: str = Field(..., description="Organization timezone")
    notifications_enabled: bool = Field(..., description="Whether organization-wide notifications are enabled")

class OrganizationSettingsUpdate(BaseModel):
    checkin_frequency: Optional[CheckinFrequency] = Field(None, description="Frequency of wellness check-ins")
    minimum_analytics_cohort_size: Optional[int] = Field(None, ge=1, description="Minimum personnel required to show analytics")
    timezone: Optional[str] = Field(None, description="Organization timezone")
    notifications_enabled: Optional[bool] = Field(None, description="Whether organization-wide notifications are enabled")

class OrganizationSettingsResponse(OrganizationSettingsBase):
    id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
