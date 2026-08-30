from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.wellness import WellnessCheckin
from app.models.audit import AuditLog
from app.schemas.wellness import WellnessCheckinCreate, WellnessCheckinResponse
from app.api.deps import get_current_user, require_personnel, require_welfare_officer

router = APIRouter()

@router.post("/checkins", response_model=dict)
def create_wellness_checkin(
    checkin_in: WellnessCheckinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel)
):
    # Check if a checkin for today already exists
    existing = db.query(WellnessCheckin).filter(
        WellnessCheckin.personnel_id == current_user.id,
        WellnessCheckin.checkin_date == checkin_in.checkin_date
    ).first()
    
    if existing:
        raise HTTPException(status_code=409, detail="Check-in already exists for this date.")
        
    checkin = WellnessCheckin(
        **checkin_in.model_dump(),
        personnel_id=current_user.id
    )
    db.add(checkin)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_WELLNESS_CHECKIN",
        resource_type="WELLNESS_CHECKIN"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(checkin)
    
    return {"id": checkin.id, "status": "recorded"}

@router.get("/me", response_model=List[WellnessCheckinResponse])
def get_my_wellness_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel)
):
    return db.query(WellnessCheckin).filter(WellnessCheckin.personnel_id == current_user.id).order_by(WellnessCheckin.checkin_date.desc()).all()

@router.get("/{personnel_id}", response_model=List[WellnessCheckinResponse])
def get_personnel_wellness(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_welfare_officer)
):
    target_user = db.query(User).filter(User.id == personnel_id, User.role == "PERSONNEL").first()
    if not target_user:
        raise HTTPException(status_code=404, detail="Personnel not found")
        
    audit = AuditLog(
        user_id=current_user.id,
        action="VIEW_PERSONNEL_WELLNESS",
        resource_type="PERSONNEL",
        resource_id=personnel_id
    )
    db.add(audit)
    db.commit()

    return db.query(WellnessCheckin).filter(WellnessCheckin.personnel_id == personnel_id).order_by(WellnessCheckin.checkin_date.desc()).all()
