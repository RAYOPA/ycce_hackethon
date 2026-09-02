from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from app.models.enums import UserRole, UserStatus

class UnitBasicResponse(BaseModel):
    id: str
    unit_code: str
    unit_name: str

    model_config = ConfigDict(from_attributes=True)

class PersonnelResponse(BaseModel):
    id: str
    user_code: str
    name: str
    unit_id: Optional[str] = None
    unit_name: Optional[str] = None
    unit: Optional[UnitBasicResponse] = None
    status: UserStatus

    model_config = ConfigDict(from_attributes=True)

class PersonnelMeResponse(BaseModel):
    id: str
    user_code: str
    name: str
    email: EmailStr
    role: UserRole
    status: UserStatus
    organization_id: str
    unit_id: Optional[str] = None
    unit: Optional[UnitBasicResponse] = None
    mobile_number: Optional[str] = None
    address: Optional[str] = None
    team: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class PersonnelListResponse(BaseModel):
    items: List[PersonnelResponse]
    page: int
    page_size: int
    total: int
