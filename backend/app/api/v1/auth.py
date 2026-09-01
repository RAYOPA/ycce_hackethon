import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    verify_password, 
    create_access_token, 
    get_password_hash,
    create_refresh_token,
    hash_refresh_token
)
from app.models.user import User
from app.models.organization import Organization
from app.models.audit import AuditLog
from app.models.auth import RefreshSession
from app.models.enums import UserStatus, AuditAction, UserRole
from app.schemas.auth import Token, LoginRequest, RefreshRequest
from app.schemas.user import UserResponse, UserRegister
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserRegister, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    org = db.query(Organization).first()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No organization found to assign the user.",
        )
        
    unique_user_code = f"P{uuid.uuid4().hex[:8].upper()}"
        
    user = User(
        email=user_in.email,
        name=user_in.name,
        user_code=unique_user_code,
        password_hash=get_password_hash(user_in.password),
        role=UserRole.PERSONNEL,
        organization_id=org.id,
        address=user_in.address,
        team=user_in.team,
        mobile_number=user_in.mobile_number,
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    audit = AuditLog(
        user_id=user.id,
        action=AuditAction.CREATE_USER,
        resource_type="USER",
        resource_id=user.id
    )
    db.add(audit)
    db.commit()
    
    return user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    user.last_login_at = datetime.now(timezone.utc)
    
    audit = AuditLog(
        user_id=user.id,
        action=AuditAction.LOGIN,
        resource_type="USER",
        resource_id=user.id
    )
    db.add(audit)

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        organization_id=user.organization_id
    )
    refresh_token = create_refresh_token()
    
    refresh_session = RefreshSession(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(refresh_session)
    db.commit()

    return {
        "access_token": access_token, 
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }

@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    token_hash = hash_refresh_token(request.refresh_token)
    session = db.query(RefreshSession).filter(RefreshSession.token_hash == token_hash).first()
    
    if not session or session.revoked_at:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
        
    if expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        
    user = session.user
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )
        
    session.last_used_at = datetime.now(timezone.utc)
    
    access_token = create_access_token(
        subject=user.id,
        role=user.role,
        organization_id=user.organization_id
    )
    
    new_refresh_token = create_refresh_token()
    new_session = RefreshSession(
        user_id=user.id,
        token_hash=hash_refresh_token(new_refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    session.revoked_at = datetime.now(timezone.utc) # Rotate token
    db.add(new_session)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": user
    }

@router.post("/logout")
def logout(request: RefreshRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    token_hash = hash_refresh_token(request.refresh_token)
    session = db.query(RefreshSession).filter(RefreshSession.token_hash == token_hash).first()
    
    if session and session.user_id == current_user.id:
        session.revoked_at = datetime.now(timezone.utc)
        
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.LOGOUT,
        resource_type="USER",
        resource_id=current_user.id
    )
    db.add(audit)
    db.commit()
    
    return {"detail": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
