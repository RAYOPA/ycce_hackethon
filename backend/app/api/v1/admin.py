from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.api.deps import get_current_user, require_admin
from app.core.security import get_password_hash

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return db.query(User).all()

@router.post("/users", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing = db.query(User).filter(
        (User.email == user_in.email) | (User.user_code == user_in.user_code)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    user = User(
        email=user_in.email,
        name=user_in.name,
        user_code=user_in.user_code,
        role=user_in.role,
        status=user_in.status,
        organization_id=user_in.organization_id,
        unit_id=user_in.unit_id,
        password_hash=get_password_hash(user_in.password)
    )
    db.add(user)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="CREATE_USER",
        resource_type="USER"
    )
    db.add(audit)
    
    db.commit()
    db.refresh(user)
    return user

@router.patch("/users/{id}", response_model=UserResponse)
def update_user(
    id: str,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_in.model_dump(exclude_unset=True)
    if "password" in update_data:
        update_data["password_hash"] = get_password_hash(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)

    audit = AuditLog(
        user_id=current_user.id,
        action="UPDATE_USER",
        resource_type="USER",
        resource_id=id
    )
    db.add(audit)

    db.commit()
    db.refresh(user)
    return user

@router.post("/users/{id}/disable")
def disable_user(
    id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.status = "INACTIVE"
    
    audit = AuditLog(
        user_id=current_user.id,
        action="DISABLE_USER",
        resource_type="USER",
        resource_id=id
    )
    db.add(audit)
    
    db.commit()
    return {"status": "disabled"}

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
    return logs
