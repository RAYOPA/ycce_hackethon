from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.enums import UserRole, UserStatus, UnitStatus, AuditAction
from app.models.user import User
from app.api.deps import get_current_user, require_admin
from app.services.admin_service import AdminService
from app.services.settings_service import SettingsService
from app.services.audit_service import AuditService
from app.schemas.admin import (
    AdminUserCreate, AdminUserUpdate, AdminUserResponse, AdminUserListResponse,
    AdminUnitCreate, AdminUnitUpdate, AdminUnitResponse,
    OrganizationAdminResponse, OrganizationAdminUpdate,
    AdminAuditLogResponse, AdminAuditLogListResponse
)
from app.schemas.settings import OrganizationSettingsResponse, OrganizationSettingsUpdate

router = APIRouter()

# ---------------------------------------------------------
# ORGANIZATION
# ---------------------------------------------------------
@router.get("/organization", response_model=OrganizationAdminResponse)
def get_organization(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    org = AdminService.get_organization(db, current_user.organization_id)
    return org

@router.patch("/organization", response_model=OrganizationAdminResponse)
def update_organization(
    update_data: OrganizationAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    org = AdminService.update_organization(db, current_user.organization_id, update_data)
    AuditService.log_action(db, current_user.id, AuditAction.UPDATE_ORGANIZATION, "Organization", org.id)
    return org

# ---------------------------------------------------------
# GOVERNANCE
# ---------------------------------------------------------
from app.models.governance import GovernancePolicy
from app.schemas.governance import GovernancePolicyResponse, GovernancePolicyUpdate

@router.get("/governance", response_model=GovernancePolicyResponse)
def get_governance_policy(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    policy = db.query(GovernancePolicy).filter(
        GovernancePolicy.organization_id == current_user.organization_id,
        GovernancePolicy.is_active == True
    ).first()
    
    if not policy:
        # Create default policy if none exists
        policy = GovernancePolicy(
            organization_id=current_user.organization_id,
            version="1.0",
            allowed_purposes=["WELLNESS_SUPPORT", "ANALYTICS"]
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
    AuditService.log_action(db, current_user.id, AuditAction.VIEW_GOVERNANCE, "GovernancePolicy", policy.id)
    return policy

@router.patch("/governance", response_model=GovernancePolicyResponse)
def update_governance_policy(
    update_data: GovernancePolicyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    policy = db.query(GovernancePolicy).filter(
        GovernancePolicy.organization_id == current_user.organization_id,
        GovernancePolicy.is_active == True
    ).first()
    
    # We could implement proper versioning by disabling the old policy and creating a new one,
    # but for simplicity we update in place and bump version (as string) or just update purposes.
    if policy:
        policy.allowed_purposes = [p.value for p in update_data.allowed_purposes]
        policy.is_active = update_data.is_active
        # Bump version simply
        try:
            v_num = float(policy.version)
            policy.version = str(round(v_num + 0.1, 1))
        except ValueError:
            policy.version = "1.0"
        
        db.commit()
        db.refresh(policy)
    else:
        policy = GovernancePolicy(
            organization_id=current_user.organization_id,
            version="1.0",
            allowed_purposes=[p.value for p in update_data.allowed_purposes]
        )
        db.add(policy)
        db.commit()
        db.refresh(policy)
        
    AuditService.log_action(db, current_user.id, AuditAction.UPDATE_GOVERNANCE, "GovernancePolicy", policy.id)
    return policy

# ---------------------------------------------------------
# UNITS
# ---------------------------------------------------------
@router.get("/units", response_model=List[AdminUnitResponse])
def list_units(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return AdminService.list_units(db, current_user.organization_id)

@router.post("/units", response_model=AdminUnitResponse, status_code=status.HTTP_201_CREATED)
def create_unit(
    data: AdminUnitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    unit = AdminService.create_unit(db, current_user.organization_id, data)
    AuditService.log_action(db, current_user.id, AuditAction.CREATE_UNIT, "Unit", unit.id)
    return unit

@router.get("/units/{unit_id}", response_model=AdminUnitResponse)
def get_unit(
    unit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return AdminService.get_unit(db, current_user.organization_id, unit_id)

@router.patch("/units/{unit_id}", response_model=AdminUnitResponse)
def update_unit(
    unit_id: str,
    data: AdminUnitUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    unit = AdminService.update_unit(db, current_user.organization_id, unit_id, data)
    AuditService.log_action(db, current_user.id, AuditAction.UPDATE_UNIT, "Unit", unit.id)
    return unit

@router.patch("/units/{unit_id}/status", response_model=AdminUnitResponse)
def change_unit_status(
    unit_id: str,
    status: UnitStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    unit = AdminService.change_unit_status(db, current_user.organization_id, unit_id, status)
    action = AuditAction.ENABLE_UNIT if status == UnitStatus.ACTIVE else AuditAction.DISABLE_UNIT
    AuditService.log_action(db, current_user.id, action, "Unit", unit.id)
    return unit

# ---------------------------------------------------------
# USERS
# ---------------------------------------------------------
@router.get("/users", response_model=AdminUserListResponse)
def list_users(
    name: Optional[str] = None,
    user_code: Optional[str] = None,
    role: Optional[UserRole] = None,
    unit_id: Optional[str] = None,
    user_status: Optional[UserStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users, total = AdminService.list_users(
        db, current_user.organization_id, name, user_code, role, unit_id, user_status, page, page_size
    )
    return {"items": users, "total": total, "page": page, "page_size": page_size}

@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = AdminService.create_user(db, current_user.organization_id, data)
    AuditService.log_action(db, current_user.id, AuditAction.CREATE_USER, "User", user.id)
    return user

@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return AdminService.get_user(db, current_user.organization_id, user_id)

@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def update_user(
    user_id: str,
    data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = AdminService.update_user(db, current_user.organization_id, user_id, data, current_user.id)
    AuditService.log_action(db, current_user.id, AuditAction.UPDATE_USER, "User", user.id)
    return user

@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
def change_user_status(
    user_id: str,
    user_status: UserStatus = Query(..., alias="status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = AdminService.change_user_status(db, current_user.organization_id, user_id, user_status, current_user.id)
    action = AuditAction.ENABLE_USER if user_status == UserStatus.ACTIVE else AuditAction.DISABLE_USER
    AuditService.log_action(db, current_user.id, action, "User", user.id)
    return user

# ---------------------------------------------------------
# SETTINGS
# ---------------------------------------------------------
@router.get("/settings", response_model=OrganizationSettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    return SettingsService.get_settings(db, current_user.organization_id)

@router.patch("/settings", response_model=OrganizationSettingsResponse)
def update_settings(
    update_data: OrganizationSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    settings = SettingsService.update_settings(db, current_user.organization_id, update_data)
    AuditService.log_action(db, current_user.id, AuditAction.UPDATE_ORGANIZATION_SETTINGS, "OrganizationSettings", settings.id)
    return settings

# ---------------------------------------------------------
# AUDIT LOGS
# ---------------------------------------------------------
@router.get("/audit-logs", response_model=AdminAuditLogListResponse)
def get_audit_logs(
    action: Optional[AuditAction] = None,
    user_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    logs, total = AdminService.get_audit_logs(
        db, current_user.organization_id, action, user_id, resource_type, start_date, end_date, page, page_size
    )
    AuditService.log_action(db, current_user.id, AuditAction.VIEW_ADMIN_AUDIT_LOGS, "AuditLog", None)
    return {"items": logs, "total": total, "page": page, "page_size": page_size}
