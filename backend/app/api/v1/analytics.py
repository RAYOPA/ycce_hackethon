from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.user import User
from app.models.enums import UserRole, InterventionStatus
from app.models.wellness import WellnessCheckin
from app.models.intervention import Intervention
from app.api.deps import get_current_user, require_commander, require_welfare_officer

router = APIRouter()

@router.get("/dashboard-overview")
def get_dashboard_overview(
    time_range: str = "30D",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only allow Admin, Commander, Welfare Officer
    if current_user.role == UserRole.PERSONNEL:
        return {"status": "error", "message": "Not authorized"}
        
    total_personnel = db.query(User).filter(User.role == UserRole.PERSONNEL).count()
    
    # Welfare Metrics (from Interventions)
    elevated_cases = db.query(Intervention).filter(Intervention.status == InterventionStatus.PENDING).count()
    follow_ups = db.query(Intervention).filter(Intervention.status == InterventionStatus.IN_PROGRESS).count()
    cleared = db.query(Intervention).filter(Intervention.status == InterventionStatus.COMPLETED).count()
    
    # Mocking trend calculation for prototyping to avoid complex SQL date grouping across dialects
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    trend_data = []
    for m in months:
        trend_data.append({
            "date": m,
            "stress": 100000 + (hash(m) % 50000), # Deterministic fake data
            "fatigue": 80000 + (hash(m) % 40000),
        })

    # Top Risk Factors (mocked data based on checkins conceptually)
    risk_factors = [
        {"name": "Sleep Quality", "value": 85, "trend": "+16.31%", "color": "#22c55e"},
        {"name": "High Workload", "value": 65, "trend": "+8.11%", "color": "#22c55e"},
        {"name": "High Stress", "value": 45, "trend": "+4.89%", "color": "#22c55e"},
    ]
    
    return {
        "status": "success",
        "data": {
            "totalPersonnel": total_personnel,
            "metrics": {
                "elevatedCases": elevated_cases,
                "followUps": follow_ups,
                "risingTrends": 21, # Mock value
                "cleared": cleared
            },
            "riskFactors": risk_factors,
            "trendData": trend_data
        }
    }

@router.get("/wellness")
def get_wellness_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    # In V1, we just return placeholder aggregation
    # In future, this will aggregate actual db data
    return {
        "status": "success",
        "data": {
            "overall_wellness_index": 78,
            "trend": "+2.4%",
            "average_sleep": 6.8,
            "average_stress": 3.2
        }
    }

@router.get("/workload")
def get_workload_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    return {
        "status": "success",
        "data": {
            "average_weekly_hours": 48.5,
            "trend": "+4.2%",
            "personnel_over_50hrs": 63,
            "average_consecutive_days": 5.8
        }
    }

@router.get("/units")
def get_unit_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    return {
        "status": "success",
        "data": [
            {"unit": "Unit A", "wellness_index": 82, "workload_hours": 45},
            {"unit": "Unit B", "wellness_index": 71, "workload_hours": 52}
        ]
    }

from pydantic import BaseModel
from typing import Dict, Any
from app.services.ai_service import ai_service

class PredictRiskPayload(BaseModel):
    deployment_duration_months: float = 0.0
    duty_duration_hrs: float = 0.0
    consecutive_duty_days: float = 0.0
    night_duty: int = 0
    leave_gap_days: float = 0.0
    training_load: float = 0.0
    sleep_hours: float = 0.0
    mood_score: float = 0.0
    workload_perception: float = 0.0
    sleep_deviation: float = 0.0
    mood_deviation: float = 0.0
    workload_deviation: float = 0.0
    consecutive_night_duties_7d: float = 0.0

@router.post("/predict-risk")
def predict_risk(
    payload: PredictRiskPayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    try:
        prediction = ai_service.predict_risk(payload.model_dump())
        return {
            "status": "success",
            "data": prediction
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

