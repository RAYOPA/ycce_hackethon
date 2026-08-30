from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserResponse
from app.api.deps import get_current_user

router = APIRouter()

@router.get("", response_model=List[UserResponse])
def get_personnel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "PERSONNEL":
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    query = db.query(User).filter(User.role == "PERSONNEL")
    
    # Commanders only see their unit or all if global, etc.
    # For now we just return personnel for welfare/commander/admin
    
    return query.all()

@router.get("/{personnel_id}", response_model=UserResponse)
def get_personnel_by_id(
    personnel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "COMMANDER":
        raise HTTPException(status_code=403, detail="Commanders cannot view individual personnel records")
        
    if current_user.role == "PERSONNEL" and current_user.id != personnel_id:
        raise HTTPException(status_code=403, detail="Can only view own profile")

    user = db.query(User).filter(User.id == personnel_id, User.role == "PERSONNEL").first()
    if not user:
        raise HTTPException(status_code=404, detail="Personnel not found")

    if current_user.role in ["WELFARE_OFFICER", "ADMINISTRATOR"]:
        audit = AuditLog(
            user_id=current_user.id,
            action="VIEW_PERSONNEL",
            resource_type="PERSONNEL",
            resource_id=personnel_id
        )
        db.add(audit)
        db.commit()

    return user
