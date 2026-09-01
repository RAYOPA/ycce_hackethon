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
    email_clean = user_in.email.strip().lower()
    user = db.query(User).filter(User.email.ilike(email_clean)).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )
    
    # Check custom user code if provided
    if user_in.user_code and user_in.user_code.strip():
        code_clean = user_in.user_code.strip()
        existing_code_user = db.query(User).filter(User.user_code.ilike(code_clean)).first()
        if existing_code_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Personnel ID / User Code is already registered.",
            )
        unique_user_code = code_clean
    else:
        unique_user_code = f"P{uuid.uuid4().hex[:8].upper()}"

    org = db.query(Organization).first()
    if not org:
        org_id = str(uuid.uuid4())
        org = Organization(id=org_id, organization_code="DEMO-ORG", name="Headquarters")
        db.add(org)
        db.commit()
        db.refresh(org)
        
    from app.models.unit import Unit
    unit = db.query(Unit).filter(Unit.organization_id == org.id).first()
    if not unit:
        unit = Unit(organization_id=org.id, unit_code="U-ALPHA", unit_name="Alpha Unit")
        db.add(unit)
        db.commit()
        db.refresh(unit)

    user_role = user_in.role if user_in.role else UserRole.PERSONNEL
        
    new_user = User(
        email=email_clean,
        name=user_in.name.strip(),
        user_code=unique_user_code,
        password_hash=get_password_hash(user_in.password),
        role=user_role,
        organization_id=org.id,
        unit_id=unit.id if unit else None,
        address=user_in.address,
        team=user_in.team,
        mobile_number=user_in.mobile_number,
        status=UserStatus.ACTIVE,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    audit = AuditLog(
        user_id=new_user.id,
        action=AuditAction.CREATE_USER,
        resource_type="USER",
        resource_id=new_user.id
    )
    db.add(audit)
    db.commit()
    
    return new_user

@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    identifier = login_data.email.strip()
    user = db.query(User).filter(
        (User.email.ilike(identifier)) | (User.user_code.ilike(identifier))
    ).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/ID or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User account is inactive"
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
