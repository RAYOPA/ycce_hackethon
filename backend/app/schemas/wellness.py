from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import date, datetime

class WellnessCheckinCreate(BaseModel):
    checkin_date: date
    sleep_hours: float = Field(..., ge=0.0, le=24.0, description="Sleep duration in hours (0 to 24)")
    sleep_quality: int = Field(..., ge=1, le=5, description="Sleep quality rating (1 to 5)")
    mood_score: int = Field(..., ge=1, le=5, description="Mood score rating (1 to 5)")
    energy_score: int = Field(..., ge=1, le=5, description="Energy level rating (1 to 5)")
    workload_score: int = Field(..., ge=1, le=5, description="Workload score rating (1 to 5)")
    stress_score: int = Field(..., ge=1, le=5, description="Stress score rating (1 to 5)")

    model_config = ConfigDict(extra="forbid")

class WellnessCheckinRecordResponse(BaseModel):
    id: str
    checkin_date: date
    status: str = "recorded"

class WellnessItemResponse(BaseModel):
    id: str
    checkin_date: date
    sleep_hours: float
    sleep_quality: int
    mood_score: int
    energy_score: int
    workload_score: int
    stress_score: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class WellnessHistoryResponse(BaseModel):
    items: List[WellnessItemResponse]
    page: int
    page_size: int
    total: int
