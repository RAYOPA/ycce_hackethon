from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from app.models.enums import UserRole, UserStatus, UnitStatus, AuditAction

# User Admin Schemas
class AdminUserCreate(BaseModel):
    user_code: str = Field(..., description="Unique code identifying the user")
    email: EmailStr
    name: str
    password: str = Field(..., min_length=8)
    role: UserRole
    unit_id: Optional[str] = None
    status: UserStatus = UserStatus.ACTIVE

class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[UserRole] = None
    unit_id: Optional[str] = None
    status: Optional[UserStatus] = None

class AdminUserResponse(BaseModel):
    id: str
    user_code: str
    email: str
    name: str
    role: UserRole
    status: UserStatus
    unit_id: Optional[str]
    organization_id: str
    created_at: datetime
    last_login_at: Optional[datetime]

    model_config = {"from_attributes": True}

class AdminUserListResponse(BaseModel):
    items: List[AdminUserResponse]
    total: int
    page: int
    page_size: int

# Unit Admin Schemas
class AdminUnitCreate(BaseModel):
    unit_code: str
    unit_name: str
    status: UnitStatus = UnitStatus.ACTIVE

class AdminUnitUpdate(BaseModel):
    unit_name: Optional[str] = None
    status: Optional[UnitStatus] = None

class AdminUnitResponse(BaseModel):
    id: str
    organization_id: str
    unit_code: str
    unit_name: str
    status: UnitStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

# Organization Admin Schemas
class OrganizationAdminResponse(BaseModel):
    id: str
    organization_code: str
    name: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class OrganizationAdminUpdate(BaseModel):
    name: str

# Audit Log Admin Schemas
class AdminAuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]

    model_config = {"from_attributes": True}

class AdminAuditLogListResponse(BaseModel):
    items: List[AdminAuditLogResponse]
    total: int
    page: int
    page_size: int
