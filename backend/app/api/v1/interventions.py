from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.intervention import Intervention
from app.models.audit import AuditLog
from app.schemas.intervention import InterventionCreate, InterventionUpdate, InterventionResponse
from app.api.deps import get_current_user, require_welfare_officer
from datetime import datetime, timezone

router = APIRouter()

@router.get("", response_model=List[InterventionResponse])
def get_interventions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    return db.query(Intervention).order_by(Intervention.created_at.desc()).all()

@router.post("", response_model=InterventionResponse)
def create_intervention(
    intervention_in: InterventionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    intervention = Intervention(
        **intervention_in.model_dump(),
        assigned_officer_id=current_user.id
    )
    db.add(intervention)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_INTERVENTION",
        resource_type="INTERVENTION"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(intervention)
    return intervention

@router.patch("/{id}", response_model=InterventionResponse)
def update_intervention(
    id: str,
    intervention_in: InterventionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    intervention = db.query(Intervention).filter(Intervention.id == id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
        
    if intervention_in.notes is not None:
        intervention.notes = intervention_in.notes
    if intervention_in.status is not None:
        intervention.status = intervention_in.status
        
    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_INTERVENTION",
        resource_type="INTERVENTION",
        resource_id=id
    )
    db.add(audit)
    
    db.commit()
    db.refresh(intervention)
    return intervention

@router.post("/{id}/complete")
def complete_intervention(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    intervention = db.query(Intervention).filter(Intervention.id == id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
        
    intervention.status = "COMPLETED"
    
    audit = AuditLog(
        user_id=current_user.id,
        action="COMPLETE_INTERVENTION",
        resource_type="INTERVENTION",
        resource_id=id
    )
    db.add(audit)
    db.commit()
    return {"status": "completed"}

@router.post("/{id}/reschedule")
def reschedule_intervention(
    id: str,
    date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    intervention = db.query(Intervention).filter(Intervention.id == id).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention not found")
        
    intervention.status = "RESCHEDULED"
    intervention.follow_up_date = date
    
    audit = AuditLog(
        user_id=current_user.id,
        action="RESCHEDULE_INTERVENTION",
        resource_type="INTERVENTION",
        resource_id=id
    )
    db.add(audit)
    db.commit()
    return {"status": "rescheduled"}
