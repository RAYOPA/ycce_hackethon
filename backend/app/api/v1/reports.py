from typing import Optional, Literal
from datetime import date
from fastapi import APIRouter, Depends, Query, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.report import (
    WellnessReportResponse,
    WorkloadReportResponse,
    UnitReportResponse,
    WelfareActivityReportResponse
)
from app.services.report_service import (
    generate_wellness_report,
    generate_workload_report,
    generate_unit_report,
    generate_welfare_activity_report,
    export_wellness_csv,
    export_workload_csv,
    export_unit_csv,
    export_welfare_activity_csv
)

router = APIRouter()

@router.get("/wellness", response_model=WellnessReportResponse, summary="Get Aggregate Wellness Report")
def get_wellness_report_endpoint(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return generate_wellness_report(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )

@router.get("/wellness/export", summary="Export Aggregate Wellness Report (CSV or JSON)")
def export_wellness_report_endpoint(
    format: Literal["csv", "json"] = Query("csv", description="Export format: csv or json"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    if format == "json":
        report = generate_wellness_report(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            unit_id=unit_id,
            ip_address=ip_address
        )
        return report

    csv_data = export_wellness_csv(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=wellness_report.csv"}
    )

@router.get("/workload", response_model=WorkloadReportResponse, summary="Get Aggregate Workload Report")
def get_workload_report_endpoint(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return generate_workload_report(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )

@router.get("/workload/export", summary="Export Aggregate Workload Report (CSV or JSON)")
def export_workload_report_endpoint(
    format: Literal["csv", "json"] = Query("csv", description="Export format: csv or json"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    if format == "json":
        report = generate_workload_report(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            unit_id=unit_id,
            ip_address=ip_address
        )
        return report

    csv_data = export_workload_csv(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=workload_report.csv"}
    )

@router.get("/units", response_model=UnitReportResponse, summary="Get Unit Aggregate Report")
def get_unit_report_endpoint(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return generate_unit_report(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        ip_address=ip_address
    )

@router.get("/units/export", summary="Export Unit Aggregate Report (CSV or JSON)")
def export_unit_report_endpoint(
    format: Literal["csv", "json"] = Query("csv", description="Export format: csv or json"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    if format == "json":
        report = generate_unit_report(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            ip_address=ip_address
        )
        return report

    csv_data = export_unit_csv(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        ip_address=ip_address
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=units_report.csv"}
    )

@router.get("/welfare-activity", response_model=WelfareActivityReportResponse, summary="Get Welfare Activity Report")
def get_welfare_activity_report_endpoint(
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    return generate_welfare_activity_report(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )

@router.get("/welfare-activity/export", summary="Export Welfare Activity Report (CSV or JSON)")
def export_welfare_activity_report_endpoint(
    format: Literal["csv", "json"] = Query("csv", description="Export format: csv or json"),
    start_date: Optional[date] = Query(None, description="Start date filter (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date filter (YYYY-MM-DD)"),
    unit_id: Optional[str] = Query(None, description="Filter by authorized unit ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    ip_address = request.client.host if request and request.client else None
    if format == "json":
        report = generate_welfare_activity_report(
            db=db,
            current_user=current_user,
            start_date=start_date,
            end_date=end_date,
            unit_id=unit_id,
            ip_address=ip_address
        )
        return report

    csv_data = export_welfare_activity_csv(
        db=db,
        current_user=current_user,
        start_date=start_date,
        end_date=end_date,
        unit_id=unit_id,
        ip_address=ip_address
    )
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=welfare_activity_report.csv"}
    )
