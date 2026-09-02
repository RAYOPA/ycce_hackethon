from typing import Optional, List
from datetime import date, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.models.user import User
from app.models.unit import Unit
from app.models.wellness import WellnessCheckin
from app.models.audit import AuditLog
from app.models.enums import UserRole, AuditAction
from app.schemas.analytics import (
    WellnessAnalyticsSummary,
    WellnessTrendPoint,
    WellnessAnalyticsResponse,
    WorkloadAnalyticsSummary,
    WorkloadTrendPoint,
    WorkloadAnalyticsResponse,
    UnitAnalyticsItem,
    UnitAnalyticsResponse
)

def _validate_analytics_access(current_user: User, unit_id: Optional[str] = None):
    """
    Validates that current user has analytics access (Commander, Welfare Officer).
    Personnel and unauthorized Administrators are strictly rejected.
    """
    if current_user.role == UserRole.PERSONNEL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personnel are not authorized to access organization analytics."
        )
    if current_user.role == UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators do not have direct access to welfare analytics."
        )
    if current_user.role in (UserRole.COMMANDER, UserRole.WELFARE_OFFICER):
        # If user has a unit constraint, ensure they cannot query another unit
        if current_user.unit_id and unit_id and current_user.unit_id != unit_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view analytics outside your assigned unit."
            )

def _resolve_date_range(start_date: Optional[date], end_date: Optional[date]) -> tuple[date, date]:
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="start_date must be less than or equal to end_date."
        )
    return start_date, end_date

def get_wellness_analytics(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> WellnessAnalyticsResponse:
    _validate_analytics_access(current_user, unit_id)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    # Record audit log for authorized analytics query
    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_WELLNESS_ANALYTICS,
        resource_type="ANALYTICS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    effective_unit_id = current_user.unit_id if current_user.unit_id else unit_id

    # Count distinct personnel contributing data
    cohort_query = db.query(func.count(func.distinct(WellnessCheckin.personnel_id))).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        cohort_query = cohort_query.filter(User.unit_id == effective_unit_id)

    active_personnel_count = cohort_query.scalar() or 0

    # Privacy firewall: Minimum cohort size enforcement
    min_cohort = settings.ANALYTICS_MIN_COHORT_SIZE
    if active_personnel_count < min_cohort:
        return WellnessAnalyticsResponse(
            insufficient_cohort=True,
            min_cohort_size=min_cohort,
            active_personnel_count=active_personnel_count,
            message=f"Cohort size too small to display aggregate statistics (minimum {min_cohort} personnel required).",
            summary=None,
            trend=[]
        )

    # Database-backed SQL Aggregation for Summary
    base_query = db.query(
        func.round(func.avg(WellnessCheckin.sleep_hours), 2).label("avg_sleep_hours"),
        func.round(func.avg(WellnessCheckin.sleep_quality), 2).label("avg_sleep_quality"),
        func.round(func.avg(WellnessCheckin.mood_score), 2).label("avg_mood_score"),
        func.round(func.avg(WellnessCheckin.energy_score), 2).label("avg_energy_score"),
        func.round(func.avg(WellnessCheckin.workload_score), 2).label("avg_workload_score"),
        func.round(func.avg(WellnessCheckin.stress_score), 2).label("avg_stress_score"),
        func.count(WellnessCheckin.id).label("checkin_count")
    ).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        base_query = base_query.filter(User.unit_id == effective_unit_id)

    summary_row = base_query.first()

    summary = WellnessAnalyticsSummary(
        average_sleep_hours=float(summary_row.avg_sleep_hours or 0.0),
        average_sleep_quality=float(summary_row.avg_sleep_quality or 0.0),
        average_mood_score=float(summary_row.avg_mood_score or 0.0),
        average_energy_score=float(summary_row.avg_energy_score or 0.0),
        average_workload_score=float(summary_row.avg_workload_score or 0.0),
        average_stress_score=float(summary_row.avg_stress_score or 0.0),
        checkin_count=int(summary_row.checkin_count or 0),
        active_personnel_count=active_personnel_count
    )

    # Daily Trend Aggregation
    trend_query = db.query(
        WellnessCheckin.checkin_date.label("date"),
        func.round(func.avg(WellnessCheckin.sleep_hours), 2).label("avg_sleep_hours"),
        func.round(func.avg(WellnessCheckin.stress_score), 2).label("avg_stress_score"),
        func.round(func.avg(WellnessCheckin.workload_score), 2).label("avg_workload_score"),
        func.count(WellnessCheckin.id).label("checkin_count")
    ).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        trend_query = trend_query.filter(User.unit_id == effective_unit_id)

    trend_rows = trend_query.group_by(WellnessCheckin.checkin_date).order_by(WellnessCheckin.checkin_date.asc()).all()

    trend = [
        WellnessTrendPoint(
            date=row.date,
            average_sleep_hours=float(row.avg_sleep_hours or 0.0),
            average_stress_score=float(row.avg_stress_score or 0.0),
            average_workload_score=float(row.avg_workload_score or 0.0),
            checkin_count=int(row.checkin_count or 0)
        )
        for row in trend_rows
    ]

    return WellnessAnalyticsResponse(
        insufficient_cohort=False,
        min_cohort_size=min_cohort,
        active_personnel_count=active_personnel_count,
        summary=summary,
        trend=trend
    )

def get_workload_analytics(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> WorkloadAnalyticsResponse:
    _validate_analytics_access(current_user, unit_id)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_WORKLOAD_ANALYTICS,
        resource_type="ANALYTICS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    effective_unit_id = current_user.unit_id if current_user.unit_id else unit_id

    # Cohort count
    cohort_query = db.query(func.count(func.distinct(WellnessCheckin.personnel_id))).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        cohort_query = cohort_query.filter(User.unit_id == effective_unit_id)

    active_personnel_count = cohort_query.scalar() or 0
    min_cohort = settings.ANALYTICS_MIN_COHORT_SIZE

    if active_personnel_count < min_cohort:
        return WorkloadAnalyticsResponse(
            insufficient_cohort=True,
            min_cohort_size=min_cohort,
            active_personnel_count=active_personnel_count,
            message=f"Cohort size too small to display aggregate statistics (minimum {min_cohort} personnel required).",
            summary=None,
            trend=[]
        )

    # SQL summary
    base_query = db.query(
        func.round(func.avg(WellnessCheckin.workload_score), 2).label("avg_workload_score"),
        func.count(WellnessCheckin.id).label("checkin_count")
    ).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        base_query = base_query.filter(User.unit_id == effective_unit_id)

    summary_row = base_query.first()

    summary = WorkloadAnalyticsSummary(
        average_workload_score=float(summary_row.avg_workload_score or 0.0),
        checkin_count=int(summary_row.checkin_count or 0),
        active_personnel_count=active_personnel_count
    )

    # SQL trend
    trend_query = db.query(
        WellnessCheckin.checkin_date.label("date"),
        func.round(func.avg(WellnessCheckin.workload_score), 2).label("avg_workload_score"),
        func.count(WellnessCheckin.id).label("checkin_count")
    ).join(
        User, WellnessCheckin.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        WellnessCheckin.checkin_date >= start_date,
        WellnessCheckin.checkin_date <= end_date
    )
    if effective_unit_id:
        trend_query = trend_query.filter(User.unit_id == effective_unit_id)

    trend_rows = trend_query.group_by(WellnessCheckin.checkin_date).order_by(WellnessCheckin.checkin_date.asc()).all()

    trend = [
        WorkloadTrendPoint(
            date=row.date,
            average_workload_score=float(row.avg_workload_score or 0.0),
            checkin_count=int(row.checkin_count or 0)
        )
        for row in trend_rows
    ]

    return WorkloadAnalyticsResponse(
        insufficient_cohort=False,
        min_cohort_size=min_cohort,
        active_personnel_count=active_personnel_count,
        summary=summary,
        trend=trend
    )

def get_unit_analytics(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    ip_address: Optional[str] = None
) -> UnitAnalyticsResponse:
    _validate_analytics_access(current_user)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_UNIT_ANALYTICS,
        resource_type="ANALYTICS",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    units_query = db.query(Unit).filter(Unit.organization_id == current_user.organization_id)
    if current_user.unit_id:
        units_query = units_query.filter(Unit.id == current_user.unit_id)

    units = units_query.order_by(Unit.unit_name.asc()).all()
    min_cohort = settings.ANALYTICS_MIN_COHORT_SIZE

    results: List[UnitAnalyticsItem] = []

    for u in units:
        # Check distinct personnel in unit
        cohort_count = db.query(func.count(func.distinct(WellnessCheckin.personnel_id))).join(
            User, WellnessCheckin.personnel_id == User.id
        ).filter(
            User.organization_id == current_user.organization_id,
            User.unit_id == u.id,
            WellnessCheckin.checkin_date >= start_date,
            WellnessCheckin.checkin_date <= end_date
        ).scalar() or 0

        if cohort_count < min_cohort:
            results.append(UnitAnalyticsItem(
                unit_id=u.id,
                unit_name=u.unit_name,
                insufficient_cohort=True,
                participating_personnel_count=cohort_count,
                checkin_count=None,
                average_sleep_hours=None,
                average_workload_score=None,
                average_stress_score=None
            ))
        else:
            stats = db.query(
                func.round(func.avg(WellnessCheckin.sleep_hours), 2).label("avg_sleep_hours"),
                func.round(func.avg(WellnessCheckin.workload_score), 2).label("avg_workload_score"),
                func.round(func.avg(WellnessCheckin.stress_score), 2).label("avg_stress_score"),
                func.count(WellnessCheckin.id).label("checkin_count")
            ).join(
                User, WellnessCheckin.personnel_id == User.id
            ).filter(
                User.organization_id == current_user.organization_id,
                User.unit_id == u.id,
                WellnessCheckin.checkin_date >= start_date,
                WellnessCheckin.checkin_date <= end_date
            ).first()

            results.append(UnitAnalyticsItem(
                unit_id=u.id,
                unit_name=u.unit_name,
                insufficient_cohort=False,
                participating_personnel_count=cohort_count,
                checkin_count=int(stats.checkin_count or 0),
                average_sleep_hours=float(stats.avg_sleep_hours or 0.0),
                average_workload_score=float(stats.avg_workload_score or 0.0),
                average_stress_score=float(stats.avg_stress_score or 0.0)
            ))

    return UnitAnalyticsResponse(
        min_cohort_size=min_cohort,
        units=results
    )
