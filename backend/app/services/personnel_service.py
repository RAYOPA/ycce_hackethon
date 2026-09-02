from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.enums import UserRole, UserStatus, AuditAction
from app.models.audit import AuditLog
from app.security.resource_access import ResourceAccess
from app.schemas.personnel import PersonnelResponse, PersonnelMeResponse, PersonnelListResponse, UnitBasicResponse

def get_personnel_list(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    unit_id: Optional[str] = None,
    status_filter: Optional[UserStatus] = None,
    page: int = 1,
    page_size: int = 20,
    ip_address: Optional[str] = None
) -> PersonnelListResponse:
    if not ResourceAccess.can_view_personnel_list(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personnel users are not permitted to view the organization personnel list."
        )

    # Organization-isolated query
    query = db.query(User).options(joinedload(User.unit)).filter(
        User.organization_id == current_user.organization_id,
        User.role == UserRole.PERSONNEL
    )

    if current_user.role == UserRole.WELFARE_OFFICER and current_user.unit_id:
        # If Welfare Officer is assigned to a specific unit, scope to that unit
        query = query.filter(User.unit_id == current_user.unit_id)

    if unit_id:
        query = query.filter(User.unit_id == unit_id)

    if status_filter:
        query = query.filter(User.status == status_filter)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter((User.name.ilike(search_term)) | (User.user_code.ilike(search_term)))

    total = query.count()

    # Pagination safety
    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    users = query.order_by(User.name.asc()).offset(offset).limit(page_size).all()

    items = []
    for u in users:
        unit_basic = UnitBasicResponse.model_validate(u.unit) if u.unit else None
        items.append(PersonnelResponse(
            id=u.id,
            user_code=u.user_code,
            name=u.name,
            unit_id=u.unit_id,
            unit_name=u.unit.unit_name if u.unit else None,
            unit=unit_basic,
            status=u.status
        ))

    # Audit log entry
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_PERSONNEL,
        resource_type="PERSONNEL_LIST",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    return PersonnelListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

def get_personnel_by_id(
    db: Session,
    current_user: User,
    personnel_id: str,
    ip_address: Optional[str] = None
) -> PersonnelResponse:
    target_user = db.query(User).options(joinedload(User.unit)).filter(
        User.id == personnel_id,
        User.organization_id == current_user.organization_id,
        User.role == UserRole.PERSONNEL
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnel not found."
        )

    if not ResourceAccess.can_view_personnel_detail(current_user, target_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this personnel profile."
        )

    # Audit log
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_PERSONNEL_PROFILE,
        resource_type="PERSONNEL",
        resource_id=target_user.id,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    unit_basic = UnitBasicResponse.model_validate(target_user.unit) if target_user.unit else None
    return PersonnelResponse(
        id=target_user.id,
        user_code=target_user.user_code,
        name=target_user.name,
        unit_id=target_user.unit_id,
        unit_name=target_user.unit.unit_name if target_user.unit else None,
        unit=unit_basic,
        status=target_user.status
    )

def get_personnel_me(db: Session, current_user: User) -> PersonnelMeResponse:
    user = db.query(User).options(joinedload(User.unit)).filter(User.id == current_user.id).first()
    unit_basic = UnitBasicResponse.model_validate(user.unit) if user.unit else None
    return PersonnelMeResponse(
        id=user.id,
        user_code=user.user_code,
        name=user.name,
        email=user.email,
        role=user.role,
        status=user.status,
        organization_id=user.organization_id,
        unit_id=user.unit_id,
        unit=unit_basic,
        mobile_number=user.mobile_number,
        address=user.address,
        team=user.team
    )
