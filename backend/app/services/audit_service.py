from sqlalchemy.orm import Session
from typing import Optional
from app.models.audit import AuditLog
from app.models.enums import AuditAction

class AuditService:
    @staticmethod
    def log_action(
        db: Session,
        user_id: str,
        action: AuditAction,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> AuditLog:
        audit = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit
