from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import date, datetime

class WellnessCheckinBase(BaseModel):
    checkin_date: date
    sleep_hours: float = Field(..., ge=0, le=24)
    sleep_quality: int = Field(..., ge=1, le=5)
    mood_score: int = Field(..., ge=1, le=5)
    energy_score: int = Field(..., ge=1, le=5)
    workload_score: int = Field(..., ge=1, le=5)
    stress_score: int = Field(..., ge=1, le=5)

class WellnessCheckinCreate(WellnessCheckinBase):
    pass

class WellnessCheckinResponse(WellnessCheckinBase):
    id: str
    personnel_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
