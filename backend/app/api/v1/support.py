from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.support import SupportRequest
from app.models.audit import AuditLog
from app.schemas.support import SupportRequestCreate, SupportRequestResponse
from app.api.deps import get_current_user, require_personnel

router = APIRouter()

@router.post("/requests", response_model=SupportRequestResponse)
def create_support_request(
    request_in: SupportRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_personnel)
):
    request = SupportRequest(
        **request_in.model_dump(),
        personnel_id=current_user.id
    )
    db.add(request)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_SUPPORT_REQUEST",
        resource_type="SUPPORT_REQUEST"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(request)
    return request

@router.get("/requests", response_model=List[SupportRequestResponse])
def get_support_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role == "PERSONNEL":
        return db.query(SupportRequest).filter(SupportRequest.personnel_id == current_user.id).order_by(SupportRequest.created_at.desc()).all()
    
    if current_user.role == "COMMANDER":
        raise HTTPException(status_code=403, detail="Commanders cannot view individual support requests")
        
    return db.query(SupportRequest).order_by(SupportRequest.created_at.desc()).all()

@router.get("/requests/{id}", response_model=SupportRequestResponse)
def get_support_request(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    request = db.query(SupportRequest).filter(SupportRequest.id == id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if current_user.role == "PERSONNEL" and request.personnel_id != current_user.id:
        raise HTTPException(status_code=403, detail="Can only view own requests")
        
    if current_user.role == "COMMANDER":
        raise HTTPException(status_code=403, detail="Commanders cannot view individual support requests")

    if current_user.role in ["WELFARE_OFFICER", "ADMINISTRATOR"]:
        audit = AuditLog(
            user_id=current_user.id,
            action="VIEW_SUPPORT_REQUEST",
            resource_type="SUPPORT_REQUEST",
            resource_id=id
        )
        db.add(audit)
        db.commit()

    return request
