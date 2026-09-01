from fastapi import HTTPException, status
from app.models.user import User

def ensure_same_organization(current_user: User, target_organization_id: str):
    """
    Ensures that the current user belongs to the same organization as the target resource.
    Raises a 403 Forbidden if the user attempts to cross organization boundaries.
    """
    if str(current_user.organization_id) != str(target_organization_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access to resources outside your organization is forbidden."
        )
