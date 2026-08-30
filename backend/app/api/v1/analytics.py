from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_commander

router = APIRouter()

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
