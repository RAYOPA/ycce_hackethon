from typing import Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.support import SupportRequest
from app.models.audit import AuditLog
from app.models.enums import UserRole, SupportRequestStatus, SupportRequestType, AuditAction, NotificationType
from app.security.privacy_policy import PrivacyPolicy
from app.security.resource_access import ResourceAccess
from app.services.notification_service import create_notification
from app.schemas.support import (
    SupportRequestCreate,
    SupportRequestCreatedResponse,
    SupportRequestSummary,
    SupportRequestResponse,
    SupportRequestListResponse
)

VALID_TRANSITIONS = {
    SupportRequestStatus.OPEN: {SupportRequestStatus.IN_REVIEW, SupportRequestStatus.CLOSED},
    SupportRequestStatus.IN_REVIEW: {SupportRequestStatus.RESOLVED, SupportRequestStatus.CLOSED},
    SupportRequestStatus.RESOLVED: {SupportRequestStatus.CLOSED},
    SupportRequestStatus.CLOSED: set()
}

def create_support_request(
    db: Session,
    current_user: User,
    request_in: SupportRequestCreate,
    ip_address: Optional[str] = None
) -> SupportRequestCreatedResponse:
    if current_user.role != UserRole.PERSONNEL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only personnel users can submit support requests."
        )

    try:
        support_req = SupportRequest(
            personnel_id=current_user.id,
            request_type=request_in.request_type,
            message=request_in.message,
            status=SupportRequestStatus.OPEN
        )
        db.add(support_req)
        db.flush()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.CREATE_SUPPORT_REQUEST,
            resource_type="SUPPORT_REQUEST",
            resource_id=support_req.id,
            ip_address=ip_address
        )
        db.add(audit)

        # Notify active Welfare Officers in the same organization
        officers = db.query(User).filter(
            User.organization_id == current_user.organization_id,
            User.role == UserRole.WELFARE_OFFICER,
            User.status == "ACTIVE"
        ).all()

        for officer in officers:
            # If officer is assigned to specific unit, only notify if matching unit
            if officer.unit_id and current_user.unit_id and officer.unit_id != current_user.unit_id:
                continue
            create_notification(
                db=db,
                user_id=officer.id,
                notification_type=NotificationType.SUPPORT,
                title="New Support Request",
                message="New welfare support request requires review.",
                related_resource=support_req.id
            )

        db.commit()
        db.refresh(support_req)

        return SupportRequestCreatedResponse(
            id=support_req.id,
            status=support_req.status,
            created_at=support_req.created_at
        )
    except Exception:
        db.rollback()
        raise

def get_support_requests(
    db: Session,
    current_user: User,
    status_filter: Optional[SupportRequestStatus] = None,
    request_type_filter: Optional[SupportRequestType] = None,
    unit_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    ip_address: Optional[str] = None
) -> SupportRequestListResponse:
    if current_user.role in (UserRole.COMMANDER, UserRole.ADMINISTRATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to individual support requests is forbidden for your role."
        )

    query = db.query(SupportRequest).join(SupportRequest.personnel).filter(
        User.organization_id == current_user.organization_id
    )

    if current_user.role == UserRole.PERSONNEL:
        # Personnel can only see their own requests
        query = query.filter(SupportRequest.personnel_id == current_user.id)
    elif current_user.role == UserRole.WELFARE_OFFICER:
        if current_user.unit_id:
            query = query.filter(User.unit_id == current_user.unit_id)
        if unit_id:
            query = query.filter(User.unit_id == unit_id)

    if status_filter:
        query = query.filter(SupportRequest.status == status_filter)
    if request_type_filter:
        query = query.filter(SupportRequest.request_type == request_type_filter)
    if start_date:
        query = query.filter(SupportRequest.created_at >= start_date)
    if end_date:
        query = query.filter(SupportRequest.created_at <= end_date)

    total = query.count()

    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    requests = query.order_by(SupportRequest.created_at.desc()).offset(offset).limit(page_size).all()

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_SUPPORT_REQUEST,
        resource_type="SUPPORT_REQUEST_QUEUE",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    items = []
    for r in requests:
        items.append(SupportRequestSummary(
            id=r.id,
            personnel_id=r.personnel_id,
            personnel_code=r.personnel.user_code if r.personnel else None,
            unit_id=r.personnel.unit_id if r.personnel else None,
            request_type=r.request_type,
            status=r.status,
            created_at=r.created_at,
            updated_at=r.updated_at
        ))

    return SupportRequestListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

def get_support_request_by_id(
    db: Session,
    current_user: User,
    request_id: str,
    ip_address: Optional[str] = None
) -> SupportRequestResponse:
    support_req = db.query(SupportRequest).options(joinedload(SupportRequest.personnel)).filter(
        SupportRequest.id == request_id
    ).first()

    if not support_req or str(support_req.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support request not found."
        )

    PrivacyPolicy.assert_can_view_support_message(current_user, support_req.personnel_id)
    ResourceAccess.assert_unit_access(current_user, support_req.personnel.unit_id)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_SUPPORT_REQUEST,
        resource_type="SUPPORT_REQUEST",
        resource_id=support_req.id,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    return SupportRequestResponse(
        id=support_req.id,
        personnel_id=support_req.personnel_id,
        personnel_code=support_req.personnel.user_code if support_req.personnel else None,
        unit_id=support_req.personnel.unit_id if support_req.personnel else None,
        request_type=support_req.request_type,
        message=support_req.message,
        status=support_req.status,
        created_at=support_req.created_at,
        updated_at=support_req.updated_at
    )

def update_support_request_status(
    db: Session,
    current_user: User,
    request_id: str,
    new_status: SupportRequestStatus,
    ip_address: Optional[str] = None
) -> SupportRequestResponse:
    if current_user.role != UserRole.WELFARE_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can update support request statuses."
        )

    support_req = db.query(SupportRequest).options(joinedload(SupportRequest.personnel)).filter(
        SupportRequest.id == request_id
    ).first()

    if not support_req or str(support_req.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Support request not found."
        )

    PrivacyPolicy.assert_can_view_support_message(current_user, support_req.personnel_id)
    ResourceAccess.assert_unit_access(current_user, support_req.personnel.unit_id)

    # Validate status transition
    allowed_next = VALID_TRANSITIONS.get(support_req.status, set())
    if new_status != support_req.status and new_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {support_req.status.value} to {new_status.value}."
        )

    try:
        support_req.status = new_status
        support_req.updated_at = datetime.now()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.UPDATE_SUPPORT_REQUEST,
            resource_type="SUPPORT_REQUEST",
            resource_id=support_req.id,
            ip_address=ip_address
        )
        db.add(audit)

        # Notify the personnel about the status update
        create_notification(
            db=db,
            user_id=support_req.personnel_id,
            notification_type=NotificationType.SUPPORT,
            title="Support Request Updated",
            message=f"Your support request status has been updated to {new_status.value}.",
            related_resource=support_req.id
        )

        db.commit()
        db.refresh(support_req)

        return SupportRequestResponse(
            id=support_req.id,
            personnel_id=support_req.personnel_id,
            personnel_code=support_req.personnel.user_code if support_req.personnel else None,
            unit_id=support_req.personnel.unit_id if support_req.personnel else None,
            request_type=support_req.request_type,
            message=support_req.message,
            status=support_req.status,
            created_at=support_req.created_at,
            updated_at=support_req.updated_at
        )
    except Exception:
        db.rollback()
        raise
