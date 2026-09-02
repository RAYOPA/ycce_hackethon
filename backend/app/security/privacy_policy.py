from typing import List, Any
from fastapi import HTTPException, status
from app.models.user import User
from app.models.enums import UserRole

class PrivacyPolicy:
    """
    Centralized privacy firewall for ManRakshak.
    Enforces rules on who can see sensitive welfare data, AI data, and admin data.
    """
    
    @staticmethod
    def assert_can_view_individual_wellness(current_user: User, target_user_id: str):
        if current_user.role == UserRole.PERSONNEL:
            if current_user.id != target_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Privacy violation: Cannot view another personnel's wellness data."
                )
        elif current_user.role == UserRole.COMMANDER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Commanders can only view aggregate wellness data."
            )
        elif current_user.role == UserRole.ADMINISTRATOR:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Administrators cannot view wellness data."
            )
        # Welfare officers can view (subject to unit/org authorization checks done elsewhere)

    @staticmethod
    def assert_can_view_support_message(current_user: User, target_user_id: str):
        if current_user.role == UserRole.PERSONNEL:
            if current_user.id != target_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Privacy violation: Cannot view another personnel's support messages."
                )
        elif current_user.role in (UserRole.COMMANDER, UserRole.ADMINISTRATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Role not permitted to view individual support messages."
            )
            
    @staticmethod
    def assert_can_view_intervention(current_user: User, target_user: User):
        if current_user.role == UserRole.PERSONNEL:
            if current_user.id != target_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Privacy violation: Cannot access another personnel's interventions."
                )
        elif current_user.role in (UserRole.COMMANDER, UserRole.ADMINISTRATOR):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Role not permitted to access individual interventions."
            )
        # For Welfare Officers, the unit restriction check is handled by ResourceAccess

    @staticmethod
    def assert_can_view_intervention_notes(current_user: User):
        if current_user.role != UserRole.WELFARE_OFFICER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: Only Welfare Officers can view intervention notes."
            )
            
    @staticmethod
    def assert_cohort_size(count: int, min_cohort_size: int):
        if count < min_cohort_size:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Privacy violation: Cohort size ({count}) is below the minimum threshold ({min_cohort_size})."
            )

class FutureAIDataPolicy:
    """
    Placeholder for future AI data privacy rules.
    AI data is strictly protected.
    """
    @staticmethod
    def assert_can_view_predictions(current_user: User):
        if current_user.role != UserRole.WELFARE_OFFICER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Privacy violation: AI predictions are restricted to Welfare Officers only."
            )
