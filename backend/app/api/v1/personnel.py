from typing import Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import UserStatus
from app.api.deps import get_current_user
from app.schemas.personnel import PersonnelResponse, PersonnelMeResponse, PersonnelListResponse
from app.services.personnel_service import get_personnel_list, get_personnel_by_id, get_personnel_me

router = APIRouter()

@router.get("", response_model=PersonnelListResponse, summary="Get Organization Personnel List")
def list_personnel(
    search: Optional[str] = Query(None, description="Search by name or personnel code"),
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    status: Optional[UserStatus] = Query(None, description="Filter by status (ACTIVE/INACTIVE)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_personnel_list(
        db=db,
        current_user=current_user,
        search=search,
        unit_id=unit_id,
        status_filter=status,
        page=page,
        page_size=page_size,
        ip_address=ip_address
    )

@router.get("/me", response_model=PersonnelMeResponse, summary="Get Current Personnel Profile")
def get_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_personnel_me(db=db, current_user=current_user)

@router.get("/{personnel_id}", response_model=PersonnelResponse, summary="Get Personnel Details by ID")
def get_personnel(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_personnel_by_id(
        db=db,
        current_user=current_user,
        personnel_id=personnel_id,
        ip_address=ip_address
    )
