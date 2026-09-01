import os
import sys
import uuid
import argparse
from datetime import date, datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Base, Organization, Unit, User, WellnessCheckin, SupportRequest, Intervention, Notification, AuditLog
from app.models.enums import UserRole, UserStatus, UnitStatus, SupportRequestType, SupportRequestStatus, InterventionActionType, InterventionStatus, NotificationType, AuditAction

def seed(reset: bool = False):
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Idempotency check / reset
        existing_org = db.query(Organization).filter(Organization.organization_code == "DEMO-ORG").first()
        if existing_org:
            if reset:
                print("Resetting demo data...")
                db.delete(existing_org) # Cascade delete will handle units and users if configured, else we need to delete manually
                # Manual cascading for safety since we disabled cascade delete on organization
                db.query(WellnessCheckin).filter(WellnessCheckin.personnel.has(User.organization_id == existing_org.id)).delete(synchronize_session=False)
                db.query(SupportRequest).filter(SupportRequest.personnel.has(User.organization_id == existing_org.id)).delete(synchronize_session=False)
                db.query(Intervention).filter(Intervention.personnel.has(User.organization_id == existing_org.id)).delete(synchronize_session=False)
                db.query(Notification).filter(Notification.user.has(User.organization_id == existing_org.id)).delete(synchronize_session=False)
                db.query(AuditLog).filter(AuditLog.user.has(User.organization_id == existing_org.id)).delete(synchronize_session=False)
                db.query(User).filter(User.organization_id == existing_org.id).delete(synchronize_session=False)
                db.query(Unit).filter(Unit.organization_id == existing_org.id).delete(synchronize_session=False)
                db.query(Organization).filter(Organization.id == existing_org.id).delete(synchronize_session=False)
                db.commit()
            else:
                print("Demo data already exists. Use --reset to overwrite.")
                return

        print("Seeding demo database...")
        # 1 organization
        org_id = str(uuid.uuid4())
        org = Organization(id=org_id, organization_code="DEMO-ORG", name="Demo Headquarters")
        db.add(org)
        db.commit()

        # 2 units
        unit1 = Unit(organization_id=org_id, unit_code="U-ALPHA", unit_name="Alpha Unit", status=UnitStatus.ACTIVE)
        unit2 = Unit(organization_id=org_id, unit_code="U-BRAVO", unit_name="Bravo Unit", status=UnitStatus.ACTIVE)
        db.add_all([unit1, unit2])
        db.commit()

        # Hash password once
        demo_password_hash = get_password_hash("demo123")

        # 1 administrator
        admin = User(
            organization_id=org_id,
            user_code="ADM-01",
            name="Demo Admin",
            email="admin@demo.com",
            password_hash=demo_password_hash,
            role=UserRole.ADMINISTRATOR,
            status=UserStatus.ACTIVE
        )
        db.add(admin)

        # 1 commander
        commander = User(
            organization_id=org_id,
            unit_id=unit1.id,
            user_code="CMD-01",
            name="Demo Commander",
            email="commander@demo.com",
            password_hash=demo_password_hash,
            role=UserRole.COMMANDER,
            status=UserStatus.ACTIVE
        )
        db.add(commander)

        # 1 welfare officer
        officer = User(
            organization_id=org_id,
            unit_id=unit1.id,
            user_code="WLF-01",
            name="Demo Welfare Officer",
            email="welfare@demo.com",
            password_hash=demo_password_hash,
            role=UserRole.WELFARE_OFFICER,
            status=UserStatus.ACTIVE
        )
        db.add(officer)

        # 2 personnel
        person1 = User(
            organization_id=org_id,
            unit_id=unit1.id,
            user_code="PER-01",
            name="Personnel One",
            email="p001@demo.com",
            password_hash=demo_password_hash,
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        person2 = User(
            organization_id=org_id,
            unit_id=unit2.id,
            user_code="PER-02",
            name="Personnel Two",
            email="p002@demo.com",
            password_hash=demo_password_hash,
            role=UserRole.PERSONNEL,
            status=UserStatus.ACTIVE
        )
        db.add_all([person1, person2])
        db.commit()

        # Seed Wellness Data
        today = date.today()
        for i in range(7):
            checkin_d = today - timedelta(days=i)
            # For P001
            db.add(WellnessCheckin(
                personnel_id=person1.id,
                checkin_date=checkin_d,
                sleep_hours=7.0,
                sleep_quality=4,
                mood_score=4,
                energy_score=4,
                workload_score=3,
                stress_score=2
            ))
            # For P002
            db.add(WellnessCheckin(
                personnel_id=person2.id,
                checkin_date=checkin_d,
                sleep_hours=6.5,
                sleep_quality=3,
                mood_score=3,
                energy_score=3,
                workload_score=4,
                stress_score=3
            ))
        db.commit()

        # Seed Support Requests
        sr1 = SupportRequest(
            personnel_id=person1.id,
            request_type=SupportRequestType.GENERAL_WELLBEING,
            message="Feeling a bit burnt out this week.",
            status=SupportRequestStatus.OPEN
        )
        sr2 = SupportRequest(
            personnel_id=person2.id,
            request_type=SupportRequestType.WORKLOAD,
            message="Requesting a review of current task assignments.",
            status=SupportRequestStatus.IN_REVIEW
        )
        sr3 = SupportRequest(
            personnel_id=person1.id,
            request_type=SupportRequestType.PERSONAL_SUPPORT,
            message="Need to discuss personal matters.",
            status=SupportRequestStatus.RESOLVED
        )
        db.add_all([sr1, sr2, sr3])
        db.commit()

        # Seed Interventions
        inv1 = Intervention(
            personnel_id=person1.id,
            assigned_officer_id=officer.id,
            action_type=InterventionActionType.WELLNESS_FOLLOWUP,
            notes="Follow up on burnout next week.",
            status=InterventionStatus.PENDING
        )
        inv2 = Intervention(
            personnel_id=person2.id,
            assigned_officer_id=officer.id,
            action_type=InterventionActionType.WORKLOAD_REVIEW,
            notes="Reviewing with commander.",
            status=InterventionStatus.IN_PROGRESS
        )
        inv3 = Intervention(
            personnel_id=person1.id,
            assigned_officer_id=officer.id,
            action_type=InterventionActionType.GENERAL_WELFARE_SUPPORT,
            notes="Issue resolved after personal support session.",
            status=InterventionStatus.COMPLETED
        )
        db.add_all([inv1, inv2, inv3])
        db.commit()

        # Seed Notifications
        n1 = Notification(
            user_id=person1.id,
            notification_type=NotificationType.FOLLOWUP,
            title="Follow-up Reminder",
            message="Please complete your wellness survey.",
            is_read=False
        )
        n2 = Notification(
            user_id=person2.id,
            notification_type=NotificationType.SUPPORT,
            title="Support Request Update",
            message="Your request is in review.",
            is_read=True
        )
        n3 = Notification(
            user_id=officer.id,
            notification_type=NotificationType.TREND,
            title="Aggregate Trend Update",
            message="Alpha unit showing increased stress.",
            is_read=False
        )
        n4 = Notification(
            user_id=admin.id,
            notification_type=NotificationType.SYSTEM,
            title="System Maintenance",
            message="Maintenance scheduled for tonight.",
            is_read=True
        )
        db.add_all([n1, n2, n3, n4])
        db.commit()

        # Seed Audit Logs
        a1 = AuditLog(user_id=admin.id, action=AuditAction.LOGIN, ip_address="10.0.0.1")
        a2 = AuditLog(user_id=officer.id, action=AuditAction.VIEW_PERSONNEL, resource_type="USER", resource_id=person1.id, ip_address="10.0.0.2")
        a3 = AuditLog(user_id=person1.id, action=AuditAction.CREATE_WELLNESS_CHECKIN, ip_address="10.0.0.3")
        a4 = AuditLog(user_id=person2.id, action=AuditAction.CREATE_SUPPORT_REQUEST, ip_address="10.0.0.4")
        a5 = AuditLog(user_id=officer.id, action=AuditAction.CREATE_INTERVENTION, resource_type="INTERVENTION", resource_id=inv1.id, ip_address="10.0.0.2")
        db.add_all([a1, a2, a3, a4, a5])
        db.commit()

        print("Database seeded successfully.")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the development database.")
    parser.add_argument("--reset", action="store_true", help="Reset existing demo data before seeding.")
    args = parser.parse_args()
    seed(reset=args.reset)
