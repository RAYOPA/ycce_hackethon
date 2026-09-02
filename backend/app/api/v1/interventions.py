from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import InterventionStatus, InterventionActionType
from app.api.deps import get_current_user, require_welfare_officer
from app.schemas.intervention import (
    InterventionCreate,
    InterventionResponse,
    InterventionUpdate,
    InterventionReschedule,
    InterventionListResponse
)
from app.services.intervention_service import (
    create_intervention,
    get_interventions,
    get_intervention_by_id,
    update_intervention,
    complete_intervention,
    reschedule_intervention
)

router = APIRouter()

@router.post("", response_model=InterventionResponse, status_code=status.HTTP_201_CREATED, summary="Create Welfare Intervention (Welfare Officer Only)")
def create_new_intervention(
    intervention_in: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return create_intervention(
        db=db,
        current_user=current_user,
        intervention_in=intervention_in,
        ip_address=ip_address
    )

@router.get("", response_model=InterventionListResponse, summary="List Interventions")
def list_all_interventions(
    personnel_id: Optional[str] = Query(None, description="Filter by personnel ID"),
    assigned_officer_id: Optional[str] = Query(None, description="Filter by assigned officer ID"),
    status: Optional[InterventionStatus] = Query(None, description="Filter by status"),
    action_type: Optional[InterventionActionType] = Query(None, description="Filter by action type"),
    unit_id: Optional[str] = Query(None, description="Filter by unit ID"),
    follow_up_date: Optional[datetime] = Query(None, description="Filter interventions due on or before date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_interventions(
        db=db,
        current_user=current_user,
        personnel_id=personnel_id,
        assigned_officer_id=assigned_officer_id,
        status_filter=status,
        action_type_filter=action_type,
        unit_id=unit_id,
        follow_up_date=follow_up_date,
        page=page,
        page_size=page_size,
        ip_address=ip_address
    )

@router.get("/{id}", response_model=InterventionResponse, summary="Get Intervention Details")
def get_single_intervention(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return get_intervention_by_id(
        db=db,
        current_user=current_user,
        intervention_id=id,
        ip_address=ip_address
    )

@router.patch("/{id}", response_model=InterventionResponse, summary="Update Intervention (Welfare Officer Only)")
def update_single_intervention(
    id: str,
    intervention_in: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return update_intervention(
        db=db,
        current_user=current_user,
        intervention_id=id,
        intervention_in=intervention_in,
        ip_address=ip_address
    )

@router.post("/{id}/complete", summary="Complete Intervention (Welfare Officer Only)")
def mark_intervention_complete(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return complete_intervention(
        db=db,
        current_user=current_user,
        intervention_id=id,
        ip_address=ip_address
    )

@router.post("/{id}/reschedule", summary="Reschedule Intervention Follow-up (Welfare Officer Only)")
def reschedule_intervention_followup(
    id: str,
    reschedule_in: InterventionReschedule,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return reschedule_intervention(
        db=db,
        current_user=current_user,
        intervention_id=id,
        reschedule_in=reschedule_in,
        ip_address=ip_address
    )
