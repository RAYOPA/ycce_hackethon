from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date

class WellnessAnalyticsSummary(BaseModel):
    average_sleep_hours: float
    average_sleep_quality: float
    average_mood_score: float
    average_energy_score: float
    average_workload_score: float
    average_stress_score: float
    checkin_count: int
    active_personnel_count: int

    model_config = ConfigDict(from_attributes=True)

class WellnessTrendPoint(BaseModel):
    date: date
    average_sleep_hours: float
    average_stress_score: float
    average_workload_score: float
    checkin_count: int

    model_config = ConfigDict(from_attributes=True)

class WellnessAnalyticsResponse(BaseModel):
    insufficient_cohort: bool = False
    min_cohort_size: int
    active_personnel_count: int
    message: Optional[str] = None
    summary: Optional[WellnessAnalyticsSummary] = None
    trend: List[WellnessTrendPoint] = []

    model_config = ConfigDict(from_attributes=True)

class WorkloadAnalyticsSummary(BaseModel):
    average_workload_score: float
    checkin_count: int
    active_personnel_count: int

    model_config = ConfigDict(from_attributes=True)

class WorkloadTrendPoint(BaseModel):
    date: date
    average_workload_score: float
    checkin_count: int

    model_config = ConfigDict(from_attributes=True)

class WorkloadAnalyticsResponse(BaseModel):
    insufficient_cohort: bool = False
    min_cohort_size: int
    active_personnel_count: int
    message: Optional[str] = None
    summary: Optional[WorkloadAnalyticsSummary] = None
    trend: List[WorkloadTrendPoint] = []

    model_config = ConfigDict(from_attributes=True)

class UnitAnalyticsItem(BaseModel):
    unit_id: str
    unit_name: str
    insufficient_cohort: bool = False
    participating_personnel_count: int
    checkin_count: Optional[int] = None
    average_sleep_hours: Optional[float] = None
    average_workload_score: Optional[float] = None
    average_stress_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class UnitAnalyticsResponse(BaseModel):
    min_cohort_size: int
    units: List[UnitAnalyticsItem]

    model_config = ConfigDict(from_attributes=True)
