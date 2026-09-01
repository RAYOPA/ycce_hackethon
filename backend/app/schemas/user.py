from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole, UserStatus

class UserBase(BaseModel):
    email: EmailStr
    name: str
    user_code: str
    role: UserRole
    status: UserStatus = UserStatus.ACTIVE
    organization_id: str
    unit_id: Optional[str] = None
    mobile_number: Optional[str] = None
    address: Optional[str] = None
    team: Optional[str] = None

class UserCreate(UserBase):
    password: str

import re
from pydantic import field_validator

class UserRegister(BaseModel):
    name: str
    user_code: str = "123456" # Hardcoded user ID as per requirements
    address: Optional[str] = None
    team: Optional[str] = None
    mobile_number: Optional[str] = None
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    status: Optional[UserStatus] = None
    unit_id: Optional[str] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
