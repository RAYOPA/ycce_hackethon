from sqlalchemy.orm import Session
from fastapi import HTTPException
import uuid

from app.models.settings import OrganizationSettings
from app.schemas.settings import OrganizationSettingsUpdate

class SettingsService:
    @staticmethod
    def get_settings(db: Session, organization_id: str) -> OrganizationSettings:
        settings = db.query(OrganizationSettings).filter(OrganizationSettings.organization_id == organization_id).first()
        if not settings:
            # Lazy create default settings for this organization
            settings = OrganizationSettings(
                id=str(uuid.uuid4()),
                organization_id=organization_id,
            )
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings

    @staticmethod
    def update_settings(db: Session, organization_id: str, update_data: OrganizationSettingsUpdate) -> OrganizationSettings:
        settings = SettingsService.get_settings(db, organization_id)
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(settings, key, value)
            
        db.commit()
        db.refresh(settings)
        return settings
