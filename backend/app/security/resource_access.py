from fastapi import HTTPException, status
from app.models.user import User
from app.models.enums import UserRole

class ResourceAccess:
    """
    Enforces unit-level and object-level authorization for resources.
    """
    
    @staticmethod
    def assert_unit_access(current_user: User, resource_unit_id: str):
        """
        Ensures the user has access to the specified unit.
        Personnel and Welfare Officers are restricted to their own unit.
        Commanders have access to all units in their organization (assuming organization scoping is done first).
        """
        if current_user.role in (UserRole.PERSONNEL, UserRole.WELFARE_OFFICER):
            if not current_user.unit_id or current_user.unit_id != resource_unit_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Authorization violation: Cannot access resources outside your assigned unit."
                )
        # Commanders and Administrators bypass unit restrictions, but must be org-scoped.

    @staticmethod
    def can_view_personnel_list(current_user: User) -> bool:
        if current_user.role == UserRole.PERSONNEL:
            return False
        return True

    @staticmethod
    def can_view_personnel_detail(current_user: User, target_user: User) -> bool:
        if current_user.role == UserRole.PERSONNEL:
            return current_user.id == target_user.id
        if current_user.role == UserRole.WELFARE_OFFICER:
            if current_user.unit_id:
                return current_user.unit_id == target_user.unit_id
            return True
        if current_user.role == UserRole.COMMANDER:
            return False # Commanders view aggregates, not individual profiles
        return True
