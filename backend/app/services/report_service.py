import io
import csv
from typing import Optional, List
from datetime import date, datetime, timezone, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.config import settings
from app.models.user import User
from app.models.unit import Unit
from app.models.wellness import WellnessCheckin
from app.models.support import SupportRequest
from app.models.intervention import Intervention
from app.models.audit import AuditLog
from app.models.enums import UserRole, AuditAction, SupportRequestStatus, InterventionStatus
from app.schemas.report import (
    WellnessReportSummary,
    WellnessReportTrendPoint,
    WellnessReportResponse,
    WorkloadReportSummary,
    WorkloadReportTrendPoint,
    WorkloadReportResponse,
    UnitReportItem,
    UnitReportResponse,
    WelfareActivitySummary,
    WelfareActivityReportResponse
)

def _validate_report_access(db: Session, current_user: User, unit_id: Optional[str] = None):
    if current_user.role == UserRole.PERSONNEL:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Personnel are not authorized to access organizational reports."
        )
    if current_user.role == UserRole.ADMINISTRATOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators do not have direct access to welfare reports."
        )
    if unit_id:
        unit = db.query(Unit).filter(Unit.id == unit_id).first()
        if not unit or unit.organization_id != current_user.organization_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unit not found in your organization."
            )
        if current_user.unit_id and current_user.unit_id != unit_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to view reports outside your assigned unit."
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

def generate_wellness_report(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> WellnessReportResponse:
    _validate_report_access(db, current_user, unit_id)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_WELLNESS_REPORT,
        resource_type="REPORT",
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
    now = datetime.now(timezone.utc)

    if active_personnel_count < min_cohort:
        return WellnessReportResponse(
            report_version="1.0",
            report_type="WELLNESS_REPORT",
            generated_at=now,
            start_date=start_date,
            end_date=end_date,
            organization_id=current_user.organization_id,
            unit_id=effective_unit_id,
            insufficient_cohort=True,
            min_cohort_size=min_cohort,
            participating_personnel_count=active_personnel_count,
            message=f"Insufficient participating personnel for privacy-preserving reporting (minimum {min_cohort} personnel required).",
            summary=None,
            trend=[]
        )

    # SQL Summary Aggregation
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

    summary = WellnessReportSummary(
        average_sleep_hours=float(summary_row.avg_sleep_hours or 0.0),
        average_sleep_quality=float(summary_row.avg_sleep_quality or 0.0),
        average_mood_score=float(summary_row.avg_mood_score or 0.0),
        average_energy_score=float(summary_row.avg_energy_score or 0.0),
        average_workload_score=float(summary_row.avg_workload_score or 0.0),
        average_stress_score=float(summary_row.avg_stress_score or 0.0),
        total_checkins=int(summary_row.checkin_count or 0),
        participating_personnel_count=active_personnel_count
    )

    # Trend Aggregation
    trend_query = db.query(
        WellnessCheckin.checkin_date.label("date"),
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
        trend_query = trend_query.filter(User.unit_id == effective_unit_id)

    trend_rows = trend_query.group_by(WellnessCheckin.checkin_date).order_by(WellnessCheckin.checkin_date.asc()).all()

    trend = [
        WellnessReportTrendPoint(
            date=row.date,
            average_sleep_hours=float(row.avg_sleep_hours or 0.0),
            average_sleep_quality=float(row.avg_sleep_quality or 0.0),
            average_mood_score=float(row.avg_mood_score or 0.0),
            average_energy_score=float(row.avg_energy_score or 0.0),
            average_workload_score=float(row.avg_workload_score or 0.0),
            average_stress_score=float(row.avg_stress_score or 0.0),
            checkin_count=int(row.checkin_count or 0)
        )
        for row in trend_rows
    ]

    return WellnessReportResponse(
        report_version="1.0",
        report_type="WELLNESS_REPORT",
        generated_at=now,
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id,
        unit_id=effective_unit_id,
        insufficient_cohort=False,
        min_cohort_size=min_cohort,
        participating_personnel_count=active_personnel_count,
        summary=summary,
        trend=trend
    )

def generate_workload_report(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> WorkloadReportResponse:
    _validate_report_access(db, current_user, unit_id)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_WORKLOAD_REPORT,
        resource_type="REPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    effective_unit_id = current_user.unit_id if current_user.unit_id else unit_id

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
    now = datetime.now(timezone.utc)

    if active_personnel_count < min_cohort:
        return WorkloadReportResponse(
            report_version="1.0",
            report_type="WORKLOAD_REPORT",
            generated_at=now,
            start_date=start_date,
            end_date=end_date,
            organization_id=current_user.organization_id,
            unit_id=effective_unit_id,
            insufficient_cohort=True,
            min_cohort_size=min_cohort,
            participating_personnel_count=active_personnel_count,
            message=f"Insufficient participating personnel for privacy-preserving reporting (minimum {min_cohort} personnel required).",
            summary=None,
            trend=[]
        )

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

    summary = WorkloadReportSummary(
        average_workload_score=float(summary_row.avg_workload_score or 0.0),
        total_checkins=int(summary_row.checkin_count or 0),
        participating_personnel_count=active_personnel_count
    )

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
        WorkloadReportTrendPoint(
            date=row.date,
            average_workload_score=float(row.avg_workload_score or 0.0),
            checkin_count=int(row.checkin_count or 0)
        )
        for row in trend_rows
    ]

    return WorkloadReportResponse(
        report_version="1.0",
        report_type="WORKLOAD_REPORT",
        generated_at=now,
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id,
        unit_id=effective_unit_id,
        insufficient_cohort=False,
        min_cohort_size=min_cohort,
        participating_personnel_count=active_personnel_count,
        summary=summary,
        trend=trend
    )

def generate_unit_report(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    ip_address: Optional[str] = None
) -> UnitReportResponse:
    _validate_report_access(db, current_user)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_UNIT_REPORT,
        resource_type="REPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    units_query = db.query(Unit).filter(Unit.organization_id == current_user.organization_id)
    if current_user.unit_id:
        units_query = units_query.filter(Unit.id == current_user.unit_id)

    units = units_query.order_by(Unit.unit_name.asc()).all()
    min_cohort = settings.ANALYTICS_MIN_COHORT_SIZE
    now = datetime.now(timezone.utc)

    results: List[UnitReportItem] = []

    for u in units:
        cohort_count = db.query(func.count(func.distinct(WellnessCheckin.personnel_id))).join(
            User, WellnessCheckin.personnel_id == User.id
        ).filter(
            User.organization_id == current_user.organization_id,
            User.unit_id == u.id,
            WellnessCheckin.checkin_date >= start_date,
            WellnessCheckin.checkin_date <= end_date
        ).scalar() or 0

        if cohort_count < min_cohort:
            results.append(UnitReportItem(
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

            results.append(UnitReportItem(
                unit_id=u.id,
                unit_name=u.unit_name,
                insufficient_cohort=False,
                participating_personnel_count=cohort_count,
                checkin_count=int(stats.checkin_count or 0),
                average_sleep_hours=float(stats.avg_sleep_hours or 0.0),
                average_workload_score=float(stats.avg_workload_score or 0.0),
                average_stress_score=float(stats.avg_stress_score or 0.0)
            ))

    return UnitReportResponse(
        report_version="1.0",
        report_type="UNIT_REPORT",
        generated_at=now,
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id,
        min_cohort_size=min_cohort,
        units=results
    )

def generate_welfare_activity_report(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> WelfareActivityReportResponse:
    _validate_report_access(db, current_user, unit_id)
    start_date, end_date = _resolve_date_range(start_date, end_date)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.VIEW_WELFARE_ACTIVITY_REPORT,
        resource_type="REPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    effective_unit_id = current_user.unit_id if current_user.unit_id else unit_id
    now = datetime.now(timezone.utc)
    today = date.today()

    # Convert start_date and end_date to datetime boundaries for created_at queries
    dt_start = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=timezone.utc)
    dt_end = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=timezone.utc)

    # Support requests queries
    sr_query = db.query(SupportRequest).join(
        User, SupportRequest.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        SupportRequest.created_at >= dt_start,
        SupportRequest.created_at <= dt_end
    )
    if effective_unit_id:
        sr_query = sr_query.filter(User.unit_id == effective_unit_id)

    total_sr = sr_query.count()
    open_sr = sr_query.filter(SupportRequest.status == SupportRequestStatus.OPEN).count()
    in_review_sr = sr_query.filter(SupportRequest.status == SupportRequestStatus.IN_REVIEW).count()
    resolved_sr = sr_query.filter(SupportRequest.status == SupportRequestStatus.RESOLVED).count()
    closed_sr = sr_query.filter(SupportRequest.status == SupportRequestStatus.CLOSED).count()

    # Interventions queries
    it_query = db.query(Intervention).join(
        User, Intervention.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        Intervention.created_at >= dt_start,
        Intervention.created_at <= dt_end
    )
    if effective_unit_id:
        it_query = it_query.filter(User.unit_id == effective_unit_id)

    total_it = it_query.count()
    pending_it = it_query.filter(Intervention.status == InterventionStatus.PENDING).count()
    completed_it = it_query.filter(Intervention.status == InterventionStatus.COMPLETED).count()
    rescheduled_it = it_query.filter(Intervention.status == InterventionStatus.RESCHEDULED).count()

    # Follow-ups
    fu_due_query = db.query(Intervention).join(
        User, Intervention.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        Intervention.follow_up_date.isnot(None),
        Intervention.follow_up_date <= today,
        Intervention.status.in_([InterventionStatus.PENDING, InterventionStatus.IN_PROGRESS, InterventionStatus.RESCHEDULED])
    )
    if effective_unit_id:
        fu_due_query = fu_due_query.filter(User.unit_id == effective_unit_id)
    followups_due = fu_due_query.count()

    fu_done_query = db.query(Intervention).join(
        User, Intervention.personnel_id == User.id
    ).filter(
        User.organization_id == current_user.organization_id,
        Intervention.follow_up_date.isnot(None),
        Intervention.status == InterventionStatus.COMPLETED,
        Intervention.updated_at >= dt_start,
        Intervention.updated_at <= dt_end
    )
    if effective_unit_id:
        fu_done_query = fu_done_query.filter(User.unit_id == effective_unit_id)
    followups_completed = fu_done_query.count()

    summary = WelfareActivitySummary(
        support_requests_received=total_sr,
        open_requests=open_sr,
        in_review_requests=in_review_sr,
        resolved_requests=resolved_sr,
        closed_requests=closed_sr,
        interventions_created=total_it,
        interventions_completed=completed_it,
        interventions_pending=pending_it,
        interventions_rescheduled=rescheduled_it,
        followups_due=followups_due,
        followups_completed=followups_completed
    )

    return WelfareActivityReportResponse(
        report_version="1.0",
        report_type="WELFARE_ACTIVITY_REPORT",
        generated_at=now,
        start_date=start_date,
        end_date=end_date,
        organization_id=current_user.organization_id,
        unit_id=effective_unit_id,
        summary=summary
    )

def export_wellness_csv(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> str:
    report = generate_wellness_report(db, current_user, start_date, end_date, unit_id, ip_address)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.EXPORT_WELLNESS_REPORT,
        resource_type="REPORT_EXPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    if report.insufficient_cohort:
        writer.writerow(["status", "message"])
        writer.writerow(["insufficient_cohort", report.message])
        return output.getvalue()

    writer.writerow([
        "date",
        "average_sleep_hours",
        "average_sleep_quality",
        "average_mood_score",
        "average_energy_score",
        "average_workload_score",
        "average_stress_score",
        "checkin_count",
        "participating_personnel_count"
    ])

    for pt in report.trend:
        writer.writerow([
            pt.date.isoformat(),
            pt.average_sleep_hours,
            pt.average_sleep_quality,
            pt.average_mood_score,
            pt.average_energy_score,
            pt.average_workload_score,
            pt.average_stress_score,
            pt.checkin_count,
            report.participating_personnel_count
        ])

    return output.getvalue()

def export_workload_csv(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> str:
    report = generate_workload_report(db, current_user, start_date, end_date, unit_id, ip_address)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.EXPORT_WORKLOAD_REPORT,
        resource_type="REPORT_EXPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    if report.insufficient_cohort:
        writer.writerow(["status", "message"])
        writer.writerow(["insufficient_cohort", report.message])
        return output.getvalue()

    writer.writerow([
        "date",
        "average_workload_score",
        "checkin_count",
        "participating_personnel_count"
    ])

    for pt in report.trend:
        writer.writerow([
            pt.date.isoformat(),
            pt.average_workload_score,
            pt.checkin_count,
            report.participating_personnel_count
        ])

    return output.getvalue()

def export_unit_csv(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    ip_address: Optional[str] = None
) -> str:
    report = generate_unit_report(db, current_user, start_date, end_date, ip_address)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.EXPORT_UNIT_REPORT,
        resource_type="REPORT_EXPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "unit_name",
        "participating_personnel_count",
        "checkin_count",
        "average_sleep_hours",
        "average_workload_score",
        "average_stress_score"
    ])

    for u in report.units:
        if u.insufficient_cohort:
            writer.writerow([
                u.unit_name,
                u.participating_personnel_count,
                "INSUFFICIENT_COHORT",
                "INSUFFICIENT_COHORT",
                "INSUFFICIENT_COHORT",
                "INSUFFICIENT_COHORT"
            ])
        else:
            writer.writerow([
                u.unit_name,
                u.participating_personnel_count,
                u.checkin_count,
                u.average_sleep_hours,
                u.average_workload_score,
                u.average_stress_score
            ])

    return output.getvalue()

def export_welfare_activity_csv(
    db: Session,
    current_user: User,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    unit_id: Optional[str] = None,
    ip_address: Optional[str] = None
) -> str:
    report = generate_welfare_activity_report(db, current_user, start_date, end_date, unit_id, ip_address)

    audit = AuditLog(
        user_id=current_user.id,
        action=AuditAction.EXPORT_WELFARE_ACTIVITY_REPORT,
        resource_type="REPORT_EXPORT",
        ip_address=ip_address
    )
    db.add(audit)
    db.commit()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["metric", "value"])
    writer.writerow(["support_requests_received", report.summary.support_requests_received])
    writer.writerow(["open_requests", report.summary.open_requests])
    writer.writerow(["in_review_requests", report.summary.in_review_requests])
    writer.writerow(["resolved_requests", report.summary.resolved_requests])
    writer.writerow(["closed_requests", report.summary.closed_requests])
    writer.writerow(["interventions_created", report.summary.interventions_created])
    writer.writerow(["interventions_completed", report.summary.interventions_completed])
    writer.writerow(["interventions_pending", report.summary.interventions_pending])
    writer.writerow(["interventions_rescheduled", report.summary.interventions_rescheduled])
    writer.writerow(["followups_due", report.summary.followups_due])
    writer.writerow(["followups_completed", report.summary.followups_completed])

    return output.getvalue()
