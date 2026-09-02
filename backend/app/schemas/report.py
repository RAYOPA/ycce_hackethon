from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import date, datetime

class WellnessReportSummary(BaseModel):
    average_sleep_hours: float
    average_sleep_quality: float
    average_mood_score: float
    average_energy_score: float
    average_workload_score: float
    average_stress_score: float
    total_checkins: int
    participating_personnel_count: int

    model_config = ConfigDict(from_attributes=True)

class WellnessReportTrendPoint(BaseModel):
    date: date
    average_sleep_hours: float
    average_sleep_quality: float
    average_mood_score: float
    average_energy_score: float
    average_workload_score: float
    average_stress_score: float
    checkin_count: int

    model_config = ConfigDict(from_attributes=True)

class WellnessReportResponse(BaseModel):
    report_version: str = "1.0"
    report_type: str = "WELLNESS_REPORT"
    generated_at: datetime
    start_date: date
    end_date: date
    organization_id: str
    unit_id: Optional[str] = None
    insufficient_cohort: bool = False
    min_cohort_size: int
    participating_personnel_count: int
    message: Optional[str] = None
    summary: Optional[WellnessReportSummary] = None
    trend: List[WellnessReportTrendPoint] = []

    model_config = ConfigDict(from_attributes=True)

class WorkloadReportSummary(BaseModel):
    average_workload_score: float
    total_checkins: int
    participating_personnel_count: int

    model_config = ConfigDict(from_attributes=True)

class WorkloadReportTrendPoint(BaseModel):
    date: date
    average_workload_score: float
    checkin_count: int

    model_config = ConfigDict(from_attributes=True)

class WorkloadReportResponse(BaseModel):
    report_version: str = "1.0"
    report_type: str = "WORKLOAD_REPORT"
    generated_at: datetime
    start_date: date
    end_date: date
    organization_id: str
    unit_id: Optional[str] = None
    insufficient_cohort: bool = False
    min_cohort_size: int
    participating_personnel_count: int
    message: Optional[str] = None
    summary: Optional[WorkloadReportSummary] = None
    trend: List[WorkloadReportTrendPoint] = []

    model_config = ConfigDict(from_attributes=True)

class UnitReportItem(BaseModel):
    unit_id: str
    unit_name: str
    insufficient_cohort: bool = False
    participating_personnel_count: int
    checkin_count: Optional[int] = None
    average_sleep_hours: Optional[float] = None
    average_workload_score: Optional[float] = None
    average_stress_score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)

class UnitReportResponse(BaseModel):
    report_version: str = "1.0"
    report_type: str = "UNIT_REPORT"
    generated_at: datetime
    start_date: date
    end_date: date
    organization_id: str
    min_cohort_size: int
    units: List[UnitReportItem]

    model_config = ConfigDict(from_attributes=True)

class WelfareActivitySummary(BaseModel):
    support_requests_received: int
    open_requests: int
    in_review_requests: int
    resolved_requests: int
    closed_requests: int
    interventions_created: int
    interventions_completed: int
    interventions_pending: int
    interventions_rescheduled: int
    followups_due: int
    followups_completed: int

    model_config = ConfigDict(from_attributes=True)

class WelfareActivityReportResponse(BaseModel):
    report_version: str = "1.0"
    report_type: str = "WELFARE_ACTIVITY_REPORT"
    generated_at: datetime
    start_date: date
    end_date: date
    organization_id: str
    unit_id: Optional[str] = None
    summary: WelfareActivitySummary

    model_config = ConfigDict(from_attributes=True)
