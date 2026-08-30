from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user, require_commander

router = APIRouter()

@router.get("")
def get_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    return [
        {
            "id": "R001",
            "title": "Monthly Organization Wellness Report",
            "date": "2026-08-01",
            "type": "AGGREGATE_WELLNESS"
        }
    ]

@router.post("")
def generate_report(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_commander)
):
    return {
        "status": "generated",
        "message": "Aggregate report generated successfully"
    }
