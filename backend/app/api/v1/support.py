from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import SupportRequestStatus, SupportRequestType
from app.api.deps import get_current_user, require_personnel
from app.schemas.support import (
    SupportRequestCreate,
    SupportRequestCreatedResponse,
    SupportRequestResponse,
    SupportRequestUpdate,
    SupportRequestListResponse
)
from app.services.support_service import (
    create_support_request,
    get_support_requests,
    get_support_request_by_id,
    update_support_request_status
)

router = APIRouter()

@router.post("/requests", response_model=SupportRequestCreatedResponse, status_code=status.HTTP_201_CREATED, summary="Submit Support Request (Personnel Only)")
def submit_support_request(
    request_in: SupportRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return create_support_request(
        db=db,
        current_user=current_user,
        request_in=request_in,
        ip_address=ip_address
    )

@router.get("/requests", response_model=SupportRequestListResponse, summary="Get Support Requests / Welfare Queue")
def list_support_requests(
    status: Optional[SupportRequestStatus] = Query(None, description="Filter by status (OPEN/IN_REVIEW/RESOLVED/CLOSED)"),
    request_type: Optional[SupportRequestType] = Query(None, description="Filter by request type"),
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    start_date: Optional[datetime] = Query(None, description="Filter start date"),
    end_date: Optional[datetime] = Query(None, description="Filter end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_support_requests(
        db=db,
        current_user=current_user,
        status_filter=status,
        request_type_filter=request_type,
        unit_id=unit_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
        ip_address=ip_address
    )

@router.get("/requests/{id}", response_model=SupportRequestResponse, summary="Get Support Request Details")
def get_single_support_request(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_support_request_by_id(
        db=db,
        current_user=current_user,
        request_id=id,
        ip_address=ip_address
    )

@router.patch("/requests/{id}", response_model=SupportRequestResponse, summary="Update Support Request Status (Welfare Officer Only)")
def update_request_status(
    id: str,
    update_in: SupportRequestUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return update_support_request_status(
        db=db,
        current_user=current_user,
        request_id=id,
        new_status=update_in.status,
        ip_address=ip_address
    )
