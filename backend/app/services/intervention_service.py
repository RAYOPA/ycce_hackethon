from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.models.user import User
from app.models.intervention import Intervention
from app.models.audit import AuditLog
from app.models.enums import UserRole, InterventionStatus, InterventionActionType, AuditAction, NotificationType
from app.security.privacy_policy import PrivacyPolicy
from app.security.resource_access import ResourceAccess
from app.services.notification_service import create_notification
from app.schemas.intervention import (
    InterventionCreate,
    InterventionSummary,
    InterventionResponse,
    InterventionUpdate,
    InterventionReschedule,
    InterventionListResponse
)

def create_intervention(
    db: Session,
    current_user: User,
    intervention_in: InterventionCreate,
    ip_address: Optional[str] = None
) -> InterventionResponse:
    if current_user.role != UserRole.WELFARE_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can create interventions."
        )

    target_user = db.query(User).filter(
        User.id == intervention_in.personnel_id,
        User.organization_id == current_user.organization_id,
        User.role == UserRole.PERSONNEL
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target personnel not found in your organization."
        )

    # Unit scope check
    if current_user.unit_id and target_user.unit_id and current_user.unit_id != target_user.unit_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to create interventions for personnel in another unit."
        )

    # Assigned officer validation
    assigned_officer_id = intervention_in.assigned_officer_id or current_user.id
    if assigned_officer_id != current_user.id:
        assigned_officer = db.query(User).filter(
            User.id == assigned_officer_id,
            User.organization_id == current_user.organization_id,
            User.role == UserRole.WELFARE_OFFICER,
            User.status == "ACTIVE"
        ).first()
        if not assigned_officer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assigned officer must be an active Welfare Officer in the same organization."
            )

    try:
        intervention = Intervention(
            personnel_id=target_user.id,
            assigned_officer_id=assigned_officer_id,
            action_type=intervention_in.action_type,
            notes=intervention_in.notes,
            follow_up_date=intervention_in.follow_up_date,
            status=InterventionStatus.PENDING
        )
        db.add(intervention)
        db.flush()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.CREATE_INTERVENTION,
            resource_type="INTERVENTION",
            resource_id=intervention.id,
            ip_address=ip_address
        )
        db.add(audit)

        # If assigned to another officer, send a notification
        if assigned_officer_id != current_user.id:
            create_notification(
                db=db,
                user_id=assigned_officer_id,
                notification_type=NotificationType.FOLLOWUP,
                title="Intervention Assigned",
                message="A new welfare intervention has been assigned to you.",
                related_resource=intervention.id
            )

        db.commit()
        db.refresh(intervention)

        return InterventionResponse.model_validate(intervention)
    except Exception:
        db.rollback()
        raise

def get_interventions(
    db: Session,
    current_user: User,
    personnel_id: Optional[str] = None,
    assigned_officer_id: Optional[str] = None,
    status_filter: Optional[InterventionStatus] = None,
    action_type_filter: Optional[InterventionActionType] = None,
    unit_id: Optional[str] = None,
    follow_up_date: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 20,
    ip_address: Optional[str] = None
) -> InterventionListResponse:
    if current_user.role in (UserRole.COMMANDER, UserRole.ADMINISTRATOR):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to welfare interventions is forbidden for your role."
        )

    query = db.query(Intervention).join(Intervention.personnel).filter(
        User.organization_id == current_user.organization_id
    )

    if current_user.role == UserRole.PERSONNEL:
        query = query.filter(Intervention.personnel_id == current_user.id)
    elif current_user.role == UserRole.WELFARE_OFFICER:
        if current_user.unit_id:
            query = query.filter(User.unit_id == current_user.unit_id)
        if unit_id:
            query = query.filter(User.unit_id == unit_id)
        if personnel_id:
            query = query.filter(Intervention.personnel_id == personnel_id)
        if assigned_officer_id:
            query = query.filter(Intervention.assigned_officer_id == assigned_officer_id)

    if status_filter:
        query = query.filter(Intervention.status == status_filter)
    if action_type_filter:
        query = query.filter(Intervention.action_type == action_type_filter)
    if follow_up_date:
        query = query.filter(Intervention.follow_up_date <= follow_up_date)

    total = query.count()

    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    interventions = query.order_by(Intervention.created_at.desc()).offset(offset).limit(page_size).all()

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_INTERVENTION,
        resource_type="INTERVENTION_LIST",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    items = [InterventionSummary.model_validate(i) for i in interventions]
    return InterventionListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

def get_intervention_by_id(
    db: Session,
    current_user: User,
    intervention_id: str,
    ip_address: Optional[str] = None
) -> InterventionResponse:
    intervention = db.query(Intervention).options(joinedload(Intervention.personnel)).filter(
        Intervention.id == intervention_id
    ).first()

    if not intervention or str(intervention.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found."
        )

    PrivacyPolicy.assert_can_view_intervention(current_user, intervention.personnel)
    ResourceAccess.assert_unit_access(current_user, intervention.personnel.unit_id)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_INTERVENTION,
        resource_type="INTERVENTION",
        resource_id=intervention.id,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    res = InterventionResponse.model_validate(intervention)
    # Hide internal notes from personnel
    if current_user.role == UserRole.PERSONNEL:
        res.notes = None
    return res

def update_intervention(
    db: Session,
    current_user: User,
    intervention_id: str,
    intervention_in: InterventionUpdate,
    ip_address: Optional[str] = None
) -> InterventionResponse:
    if current_user.role != UserRole.WELFARE_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can update interventions."
        )

    intervention = db.query(Intervention).options(joinedload(Intervention.personnel)).filter(
        Intervention.id == intervention_id
    ).first()

    if not intervention or str(intervention.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found."
        )

    PrivacyPolicy.assert_can_view_intervention(current_user, intervention.personnel)
    ResourceAccess.assert_unit_access(current_user, intervention.personnel.unit_id)

    try:
        if intervention_in.action_type is not None:
            intervention.action_type = intervention_in.action_type
        if intervention_in.notes is not None:
            intervention.notes = intervention_in.notes
        if intervention_in.follow_up_date is not None:
            intervention.follow_up_date = intervention_in.follow_up_date
        if intervention_in.status is not None:
            intervention.status = intervention_in.status
        if intervention_in.assigned_officer_id is not None:
            assigned_officer = db.query(User).filter(
                User.id == intervention_in.assigned_officer_id,
                User.organization_id == current_user.organization_id,
                User.role == UserRole.WELFARE_OFFICER,
                User.status == "ACTIVE"
            ).first()
            if not assigned_officer:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Assigned officer must be an active Welfare Officer in the same organization."
                )
            intervention.assigned_officer_id = intervention_in.assigned_officer_id

        intervention.updated_at = datetime.now()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.UPDATE_INTERVENTION,
            resource_type="INTERVENTION",
            resource_id=intervention.id,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(intervention)

        return InterventionResponse.model_validate(intervention)
    except Exception:
        db.rollback()
        raise

def complete_intervention(
    db: Session,
    current_user: User,
    intervention_id: str,
    ip_address: Optional[str] = None
) -> dict:
    if current_user.role != UserRole.WELFARE_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can complete interventions."
        )

    intervention = db.query(Intervention).options(joinedload(Intervention.personnel)).filter(
        Intervention.id == intervention_id
    ).first()

    if not intervention or str(intervention.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found."
        )

    PrivacyPolicy.assert_can_view_intervention(current_user, intervention.personnel)
    ResourceAccess.assert_unit_access(current_user, intervention.personnel.unit_id)

    try:
        intervention.status = InterventionStatus.COMPLETED
        intervention.updated_at = datetime.now()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.COMPLETE_INTERVENTION,
            resource_type="INTERVENTION",
            resource_id=intervention.id,
            ip_address=ip_address
        )
        db.add(audit)

        create_notification(
            db=db,
            user_id=intervention.personnel_id,
            notification_type=NotificationType.FOLLOWUP,
            title="Intervention Completed",
            message="Welfare intervention has been completed.",
            related_resource=intervention.id
        )

        db.commit()
        return {"status": "completed"}
    except Exception:
        db.rollback()
        raise

def reschedule_intervention(
    db: Session,
    current_user: User,
    intervention_id: str,
    reschedule_in: InterventionReschedule,
    ip_address: Optional[str] = None
) -> dict:
    if current_user.role != UserRole.WELFARE_OFFICER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Welfare Officers can reschedule interventions."
        )

    intervention = db.query(Intervention).options(joinedload(Intervention.personnel)).filter(
        Intervention.id == intervention_id
    ).first()

    if not intervention or str(intervention.personnel.organization_id) != str(current_user.organization_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention not found."
        )

    PrivacyPolicy.assert_can_view_intervention(current_user, intervention.personnel)
    ResourceAccess.assert_unit_access(current_user, intervention.personnel.unit_id)

    try:
        intervention.status = InterventionStatus.RESCHEDULED
        intervention.follow_up_date = reschedule_in.follow_up_date
        intervention.updated_at = datetime.now()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.RESCHEDULE_INTERVENTION,
            resource_type="INTERVENTION",
            resource_id=intervention.id,
            ip_address=ip_address
        )
        db.add(audit)

        create_notification(
            db=db,
            user_id=intervention.personnel_id,
            notification_type=NotificationType.FOLLOWUP,
            title="Follow-up Rescheduled",
            message="Your welfare follow-up has been rescheduled.",
            related_resource=intervention.id
        )

        db.commit()
        return {"status": "rescheduled"}
    except Exception:
        db.rollback()
        raise

def get_due_followups(
    db: Session,
    organization_id: str,
    officer_id: Optional[str] = None,
    due_date: Optional[datetime] = None
) -> List[Intervention]:
    query = db.query(Intervention).join(Intervention.personnel).filter(
        User.organization_id == organization_id,
        Intervention.status.in_([InterventionStatus.PENDING, InterventionStatus.RESCHEDULED, InterventionStatus.IN_PROGRESS])
    )
    if officer_id:
        query = query.filter(Intervention.assigned_officer_id == officer_id)
    if due_date:
        query = query.filter(Intervention.follow_up_date <= due_date)
    return query.order_by(Intervention.follow_up_date.asc()).all()
