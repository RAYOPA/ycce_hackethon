from typing import Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Query
from app.models.user import User

class OrganizationScope:
    """
    Enforces organization isolation at the query and object level.
    """
    
    @staticmethod
    def assert_same_organization(current_user: User, resource_organization_id: str):
        if current_user.organization_id != resource_organization_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Security violation: Cross-organization access is strictly forbidden."
            )
            
    @staticmethod
    def filter_query(query: Query, model: Any, current_user: User) -> Query:
        """
        Appends the organization_id filter to a SQLAlchemy query.
        Assumes the model has an `organization_id` attribute.
        """
        if not hasattr(model, 'organization_id'):
            raise ValueError(f"Model {model.__name__} does not have an organization_id attribute.")
        return query.filter(model.organization_id == current_user.organization_id)
