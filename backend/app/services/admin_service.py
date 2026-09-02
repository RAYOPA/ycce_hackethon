from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone

from app.models.user import User
from app.models.unit import Unit
from app.models.organization import Organization
from app.models.audit import AuditLog
from app.models.enums import UserRole, UserStatus, UnitStatus, AuditAction
from app.schemas.admin import (
    AdminUserCreate, AdminUserUpdate,
    AdminUnitCreate, AdminUnitUpdate,
    OrganizationAdminUpdate
)
from app.core.security import get_password_hash

class AdminService:
    @staticmethod
    def get_organization(db: Session, org_id: str) -> Organization:
        org = db.query(Organization).filter(Organization.id == org_id).first()
        if not org:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return org

    @staticmethod
    def update_organization(db: Session, org_id: str, update_data: OrganizationAdminUpdate) -> Organization:
        org = AdminService.get_organization(db, org_id)
        org.name = update_data.name
        db.commit()
        db.refresh(org)
        return org

    @staticmethod
    def list_units(db: Session, org_id: str) -> List[Unit]:
        return db.query(Unit).filter(Unit.organization_id == org_id).all()

    @staticmethod
    def get_unit(db: Session, org_id: str, unit_id: str) -> Unit:
        unit = db.query(Unit).filter(Unit.id == unit_id, Unit.organization_id == org_id).first()
        if not unit:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unit not found")
        return unit

    @staticmethod
    def create_unit(db: Session, org_id: str, data: AdminUnitCreate) -> Unit:
        # Check if unit code already exists in this org
        existing = db.query(Unit).filter(Unit.organization_id == org_id, Unit.unit_code == data.unit_code).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unit code already exists in this organization")
        
        unit = Unit(
            organization_id=org_id,
            unit_code=data.unit_code,
            unit_name=data.unit_name,
            status=data.status
        )
        db.add(unit)
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def update_unit(db: Session, org_id: str, unit_id: str, data: AdminUnitUpdate) -> Unit:
        unit = AdminService.get_unit(db, org_id, unit_id)
        if data.unit_name is not None:
            unit.unit_name = data.unit_name
        if data.status is not None:
            unit.status = data.status
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def change_unit_status(db: Session, org_id: str, unit_id: str, new_status: UnitStatus) -> Unit:
        unit = AdminService.get_unit(db, org_id, unit_id)
        unit.status = new_status
        db.commit()
        db.refresh(unit)
        return unit

    @staticmethod
    def list_users(
        db: Session,
        org_id: str,
        name: Optional[str] = None,
        user_code: Optional[str] = None,
        role: Optional[UserRole] = None,
        unit_id: Optional[str] = None,
        status: Optional[UserStatus] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[User], int]:
        query = db.query(User).filter(User.organization_id == org_id)
        
        if name:
            query = query.filter(User.name.ilike(f"%{name}%"))
        if user_code:
            query = query.filter(User.user_code == user_code)
        if role:
            query = query.filter(User.role == role)
        if unit_id:
            query = query.filter(User.unit_id == unit_id)
        if status:
            query = query.filter(User.status == status)

        total = query.count()
        users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return users, total

    @staticmethod
    def get_user(db: Session, org_id: str, user_id: str) -> User:
        user = db.query(User).filter(User.id == user_id, User.organization_id == org_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    @staticmethod
    def create_user(db: Session, org_id: str, data: AdminUserCreate) -> User:
        # Check duplicates
        existing_email = db.query(User).filter(User.email == data.email).first()
        if existing_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        existing_code = db.query(User).filter(User.user_code == data.user_code).first()
        if existing_code:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User code already registered")

        # Validate unit
        if data.unit_id:
            AdminService.get_unit(db, org_id, data.unit_id)

        user = User(
            organization_id=org_id,
            user_code=data.user_code,
            email=data.email,
            name=data.name,
            password_hash=get_password_hash(data.password),
            role=data.role,
            status=data.status,
            unit_id=data.unit_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_user(db: Session, org_id: str, user_id: str, data: AdminUserUpdate, admin_user_id: str) -> User:
        user = AdminService.get_user(db, org_id, user_id)
        
        if data.unit_id is not None:
            AdminService.get_unit(db, org_id, data.unit_id)
            user.unit_id = data.unit_id
            
        if data.name is not None:
            user.name = data.name
            
        if data.status is not None:
            AdminService.change_user_status(db, org_id, user_id, data.status, admin_user_id)
            
        if data.role is not None and data.role != user.role:
            AdminService.change_user_role(db, org_id, user_id, data.role, admin_user_id)

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_user_status(db: Session, org_id: str, user_id: str, new_status: UserStatus, admin_user_id: str) -> User:
        user = AdminService.get_user(db, org_id, user_id)
        
        # Protect last admin
        if new_status == UserStatus.INACTIVE and user.role == UserRole.ADMINISTRATOR:
            active_admins = db.query(User).filter(
                User.organization_id == org_id, 
                User.role == UserRole.ADMINISTRATOR,
                User.status == UserStatus.ACTIVE,
                User.id != user_id
            ).count()
            if active_admins == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate the last active administrator")
        
        user.status = new_status
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_user_role(db: Session, org_id: str, user_id: str, new_role: UserRole, admin_user_id: str) -> User:
        user = AdminService.get_user(db, org_id, user_id)
        
        if user.id == admin_user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role")
            
        # Protect last admin
        if user.role == UserRole.ADMINISTRATOR and new_role != UserRole.ADMINISTRATOR:
            active_admins = db.query(User).filter(
                User.organization_id == org_id, 
                User.role == UserRole.ADMINISTRATOR,
                User.status == UserStatus.ACTIVE,
                User.id != user_id
            ).count()
            if active_admins == 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the last active administrator")

        user.role = new_role
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def get_audit_logs(
        db: Session,
        org_id: str,
        action: Optional[AuditAction] = None,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[AuditLog], int]:
        # Strict Isolation: We must ensure we only return audit logs belonging to users in this organization
        # To do this, we join with User
        query = db.query(AuditLog).join(User, AuditLog.user_id == User.id).filter(User.organization_id == org_id)

        if action:
            query = query.filter(AuditLog.action == action)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        total = query.count()
        logs = query.order_by(AuditLog.timestamp.desc()).offset((page - 1) * page_size).limit(page_size).all()
        return logs, total
