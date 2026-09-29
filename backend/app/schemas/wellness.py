from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import List, Optional
from datetime import date, datetime

class WellnessCheckinCreate(BaseModel):
    checkin_date: date = Field(default_factory=date.today)
    sleep_hours: float = Field(default=7.0, ge=0.0, le=24.0, description="Sleep duration in hours (0 to 24)")
    sleep_quality: Optional[int] = Field(default=None, ge=1, le=5, description="Sleep quality rating (1 to 5)")
    mood_score: Optional[int] = Field(default=None, ge=1, le=5, description="Mood score rating (1 to 5)")
    energy_score: Optional[int] = Field(default=None, ge=1, le=5, description="Energy level rating (1 to 5)")
    workload_score: Optional[int] = Field(default=3, ge=1, le=5, description="Workload score rating (1 to 5)")
    stress_score: Optional[int] = Field(default=None, ge=1, le=5, description="Stress score rating (1 to 5)")

    # Mobile / Legacy aliases
    physical_score: Optional[int] = None
    mental_score: Optional[int] = None
    stress_level: Optional[str] = None
    notes: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def reconcile_fields(cls, data):
        if not isinstance(data, dict):
            return data

        if "personnel_id" in data:
            raise ValueError("Direct assignment of personnel_id is strictly forbidden.")

        # Default checkin_date to today if not provided
        if not data.get("checkin_date"):
            data["checkin_date"] = date.today()

        # Map physical_score -> energy_score if not explicitly provided
        if data.get("energy_score") is None:
            if data.get("physical_score") is not None:
                data["energy_score"] = int(data["physical_score"])
            else:
                data["energy_score"] = 3

        # Map mental_score -> mood_score if not explicitly provided
        if data.get("mood_score") is None:
            if data.get("mental_score") is not None:
                data["mood_score"] = int(data["mental_score"])
            else:
                data["mood_score"] = 3

        # Map stress_level -> stress_score if not explicitly provided
        if data.get("stress_score") is None:
            raw_stress = data.get("stress_level")
            if raw_stress is not None:
                stress_str = str(raw_stress).strip().upper()
                if stress_str in ("HIGH", "5", "4"):
                    data["stress_score"] = 5
                elif stress_str in ("MODERATE", "MEDIUM", "3"):
                    data["stress_score"] = 3
                elif stress_str in ("LOW", "1", "2"):
                    data["stress_score"] = 1
                else:
                    data["stress_score"] = 3
            else:
                data["stress_score"] = 3

        # Default sleep_quality if not provided
        if data.get("sleep_quality") is None:
            data["sleep_quality"] = 3

        return data

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

    # Mobile compatibility fields
    physical_score: Optional[int] = None
    mental_score: Optional[int] = None
    stress_level: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="after")
    def populate_compat_fields(self):
        if self.physical_score is None:
            self.physical_score = self.energy_score
        if self.mental_score is None:
            self.mental_score = self.mood_score
        if self.stress_level is None:
            if self.stress_score >= 4:
                self.stress_level = "HIGH"
            elif self.stress_score == 3:
                self.stress_level = "MODERATE"
            else:
                self.stress_level = "LOW"
        return self

class WellnessHistoryResponse(BaseModel):
    items: List[WellnessItemResponse]
    page: int
    page_size: int
    total: int
