from typing import Optional
from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.organization import Organization
from app.models.wellness import WellnessCheckin
from app.models.audit import AuditLog
from app.models.enums import UserRole, CheckinFrequency, AuditAction
from app.security.privacy_policy import PrivacyPolicy
from app.schemas.wellness import (
    WellnessCheckinCreate,
    WellnessCheckinRecordResponse,
    WellnessItemResponse,
    WellnessHistoryResponse
)

def create_checkin(
    db: Session,
    current_user: User,
    checkin_in: WellnessCheckinCreate,
    ip_address: Optional[str] = None
) -> WellnessCheckinRecordResponse:
    if current_user.role != UserRole.PERSONNEL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only personnel users can record daily wellness check-ins."
        )

    # Check Organization frequency configuration
    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    frequency_policy = org.wellness_checkin_frequency if org else CheckinFrequency.DAILY

    if frequency_policy == CheckinFrequency.DAILY:
        existing = db.query(WellnessCheckin).filter(
            WellnessCheckin.personnel_id == current_user.id,
            WellnessCheckin.checkin_date == checkin_in.checkin_date
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A wellness check-in has already been recorded for this date."
            )

    try:
        checkin = WellnessCheckin(
            personnel_id=current_user.id,
            checkin_date=checkin_in.checkin_date,
            sleep_hours=checkin_in.sleep_hours,
            sleep_quality=checkin_in.sleep_quality,
            mood_score=checkin_in.mood_score,
            energy_score=checkin_in.energy_score,
            workload_score=checkin_in.workload_score,
            stress_score=checkin_in.stress_score
        )
        db.add(checkin)
        db.flush()

        audit = AuditLog(
            user_id=current_user.id,
            action=AuditAction.CREATE_WELLNESS_CHECKIN,
            resource_type="WELLNESS_CHECKIN",
            resource_id=checkin.id,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(checkin)

        return WellnessCheckinRecordResponse(
            id=checkin.id,
            checkin_date=checkin.checkin_date,
            status="recorded"
        )
    except Exception:
        db.rollback()
        raise

def get_my_wellness_history(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    ip_address: Optional[str] = None
) -> WellnessHistoryResponse:
    if current_user.role != UserRole.PERSONNEL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only personnel users have personal wellness history."
        )

    if start_date and end_date and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be greater than or equal to start_date."
        )

    query = db.query(WellnessCheckin).filter(WellnessCheckin.personnel_id == current_user.id)

    if start_date:
        query = query.filter(WellnessCheckin.checkin_date >= start_date)
    if end_date:
        query = query.filter(WellnessCheckin.checkin_date <= end_date)

    total = query.count()

    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    records = query.order_by(
        WellnessCheckin.checkin_date.desc(),
        WellnessCheckin.created_at.desc()
    ).offset(offset).limit(page_size).all()

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_OWN_WELLNESS,
        resource_type="WELLNESS_HISTORY",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    items = [WellnessItemResponse.model_validate(r) for r in records]
    return WellnessHistoryResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )

def get_individual_wellness(
    db: Session,
    current_user: User,
    personnel_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 20,
    ip_address: Optional[str] = None
) -> WellnessHistoryResponse:
    target_user = db.query(User).filter(
        User.id == personnel_id,
        User.organization_id == current_user.organization_id,
        User.role == UserRole.PERSONNEL
    ).first()

    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnel not found."
        )

    PrivacyPolicy.assert_can_view_individual_wellness(current_user, target_user.id)

    if start_date and end_date and end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="end_date must be greater than or equal to start_date."
        )

    query = db.query(WellnessCheckin).filter(WellnessCheckin.personnel_id == target_user.id)

    if start_date:
        query = query.filter(WellnessCheckin.checkin_date >= start_date)
    if end_date:
        query = query.filter(WellnessCheckin.checkin_date <= end_date)

    total = query.count()

    page = max(1, page)
    page_size = min(max(1, page_size), 100)
    offset = (page - 1) * page_size

    records = query.order_by(
        WellnessCheckin.checkin_date.desc(),
        WellnessCheckin.created_at.desc()
    ).offset(offset).limit(page_size).all()

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_INDIVIDUAL_WELLNESS,
        resource_type="PERSONNEL_WELLNESS",
        resource_id=target_user.id,
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    items = [WellnessItemResponse.model_validate(r) for r in records]
    return WellnessHistoryResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total
    )
