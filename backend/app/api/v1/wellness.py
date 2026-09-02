from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_personnel
from app.schemas.wellness import (
    WellnessCheckinCreate,
    WellnessCheckinRecordResponse,
    WellnessHistoryResponse
)
from app.services.wellness_service import (
    create_checkin,
    get_my_wellness_history,
    get_individual_wellness
)

router = APIRouter()

@router.post("/checkins", response_model=WellnessCheckinRecordResponse, status_code=status.HTTP_201_CREATED, summary="Record Daily Wellness Check-in")
def record_wellness_checkin(
    checkin_in: WellnessCheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return create_checkin(
        db=db,
        current_user=current_user,
        checkin_in=checkin_in,
        ip_address=ip_address
    )

@router.get("/me", response_model=WellnessHistoryResponse, summary="Get Current User's Wellness Check-in History")
def get_my_history(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_my_wellness_history(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        ip_address=ip_address
    )

@router.get("/{personnel_id}", response_model=WellnessHistoryResponse, summary="Get Individual Personnel Wellness History (Welfare Officer Only)")
def get_personnel_wellness(
    personnel_id: str,
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_individual_wellness(
        db=db,
        current_user=current_user,
        personnel_id=personnel_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        ip_address=ip_address
    )
