import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from app.core.config import settings
from app.models import Base, Organization, Unit, User, WellnessCheckin, SupportRequest, Intervention, Notification, AuditLog
from app.models.enums import UserRole, UserStatus, UnitStatus, SupportRequestType, SupportRequestStatus, InterventionActionType, InterventionStatus, NotificationType, AuditAction
from app.core.security import verify_password
import uuid
from datetime import date

engine = create_engine(settings.DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_organization_creation(db):
    org = Organization(organization_code="ORG1", name="Test Org")
    db.add(org)
    db.commit()
    db.refresh(org)
    assert org.id is not None
    assert org.organization_code == "ORG1"
    
def test_unit_creation(db):
    org = db.query(Organization).first()
    unit = Unit(organization_id=org.id, unit_code="U1", unit_name="Test Unit", status=UnitStatus.ACTIVE)
    db.add(unit)
    db.commit()
    db.refresh(unit)
    assert unit.id is not None
    assert unit.organization_id == org.id

def test_user_creation_and_password(db):
    org = db.query(Organization).first()
    unit = db.query(Unit).first()
    
    from app.core.security import get_password_hash
    hashed = get_password_hash("demo123")
    
    user = User(
        organization_id=org.id, 
        unit_id=unit.id, 
        user_code="USR1", 
        name="Test User", 
        email="test@example.com", 
        password_hash=hashed, 
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    assert user.id is not None
    assert user.role == UserRole.PERSONNEL
    assert user.password_hash != "demo123"
    assert verify_password("demo123", user.password_hash) is True

def test_duplicate_user_email_fails(db):
    org = db.query(Organization).first()
    unit = db.query(Unit).first()
    
    user = User(
        organization_id=org.id, 
        unit_id=unit.id, 
        user_code="USR2", 
        name="Test User 2", 
        email="test@example.com", # Same email as previous test
        password_hash="hash", 
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_duplicate_user_code_fails(db):
    org = db.query(Organization).first()
    unit = db.query(Unit).first()
    
    user = User(
        organization_id=org.id, 
        unit_id=unit.id, 
        user_code="USR1", # Same code as previous test
        name="Test User 3", 
        email="test3@example.com", 
        password_hash="hash", 
        role=UserRole.PERSONNEL,
        status=UserStatus.ACTIVE
    )
    db.add(user)
    with pytest.raises(IntegrityError):
        db.commit()
    db.rollback()

def test_wellness_checkin(db):
    user = db.query(User).filter(User.user_code == "USR1").first()
    checkin = WellnessCheckin(
        personnel_id=user.id,
        checkin_date=date.today(),
        sleep_hours=8.0,
        sleep_quality=4,
        mood_score=4,
        energy_score=4,
        workload_score=3,
        stress_score=2
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    assert checkin.id is not None

def test_support_request(db):
    user = db.query(User).filter(User.user_code == "USR1").first()
    req = SupportRequest(
        personnel_id=user.id,
        request_type=SupportRequestType.GENERAL_WELLBEING,
        message="Need support",
        status=SupportRequestStatus.OPEN
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    assert req.id is not None

def test_intervention(db):
    user = db.query(User).filter(User.user_code == "USR1").first()
    officer = User(
        organization_id=user.organization_id,
        unit_id=user.unit_id,
        user_code="OFF1",
        name="Officer",
        email="officer@example.com",
        password_hash="hash",
        role=UserRole.WELFARE_OFFICER,
        status=UserStatus.ACTIVE
    )
    db.add(officer)
    db.commit()
    
    intervention = Intervention(
        personnel_id=user.id,
        assigned_officer_id=officer.id,
        action_type=InterventionActionType.WORKLOAD_REVIEW,
        notes="Reviewing workload",
        status=InterventionStatus.PENDING
    )
    db.add(intervention)
    db.commit()
    db.refresh(intervention)
    assert intervention.id is not None

def test_notification(db):
    user = db.query(User).filter(User.user_code == "USR1").first()
    notif = Notification(
        user_id=user.id,
        notification_type=NotificationType.SYSTEM,
        title="Welcome",
        message="Hello world",
        is_read=False
    )
    db.add(notif)
    db.commit()
    db.refresh(notif)
    assert notif.id is not None

def test_audit_log(db):
    user = db.query(User).filter(User.user_code == "USR1").first()
    audit = AuditLog(
        user_id=user.id,
        action=AuditAction.LOGIN,
        resource_type="USER",
        resource_id=user.id,
        ip_address="127.0.0.1"
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    assert audit.id is not None

