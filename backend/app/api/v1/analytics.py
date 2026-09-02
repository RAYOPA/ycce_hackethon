from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.analytics import (
    WellnessAnalyticsResponse,
    WorkloadAnalyticsResponse,
    UnitAnalyticsResponse
)
from app.services.analytics_service import (
    get_wellness_analytics,
    get_workload_analytics,
    get_unit_analytics
)

router = APIRouter()

@router.get("/wellness", response_model=WellnessAnalyticsResponse, summary="Get Organization Aggregate Wellness Analytics")
def read_wellness_analytics(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_wellness_analytics(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )

@router.get("/workload", response_model=WorkloadAnalyticsResponse, summary="Get Organization Aggregate Workload Analytics")
def read_workload_analytics(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_workload_analytics(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )

@router.get("/units", response_model=UnitAnalyticsResponse, summary="Get Unit-level Aggregate Analytics")
def read_unit_analytics(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_unit_analytics(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        ip_address=ip_address
    )
