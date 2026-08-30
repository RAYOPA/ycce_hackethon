import sys
import os
import uuid
import random
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.organization import Organization
from app.models.unit import Unit
from app.models.user import User
from app.models.wellness import WellnessCheckin

def seed():
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    print("Seeding database...")
    
    # Create Organization
    org = Organization(
        organization_code="ORG001",
        name="Demo Organization"
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    
    # Create Units
    units = []
    for i in range(1, 5):
        unit = Unit(
            organization_id=org.id,
            unit_code=f"U00{i}",
            unit_name=f"Unit {chr(64+i)}"
        )
        db.add(unit)
        units.append(unit)
    
    db.commit()
    for unit in units:
        db.refresh(unit)

    password_hash = get_password_hash("demo123")

    # Demo Accounts
    admin = User(
        organization_id=org.id,
        user_code="A001",
        name="Demo Admin",
        email="admin@demo.com",
        password_hash=password_hash,
        role="ADMINISTRATOR"
    )
    db.add(admin)

    commander = User(
        organization_id=org.id,
        user_code="C001",
        name="Demo Commander",
        email="commander@demo.com",
        password_hash=password_hash,
        role="COMMANDER"
    )
    db.add(commander)

    welfare = User(
        organization_id=org.id,
        unit_id=units[0].id,
        user_code="W001",
        name="Demo Welfare Officer",
        email="welfare@demo.com",
        password_hash=password_hash,
        role="WELFARE_OFFICER"
    )
    db.add(welfare)

    personnel_demo = User(
        organization_id=org.id,
        unit_id=units[0].id,
        user_code="P001",
        name="Demo Personnel",
        email="p001@demo.com",
        password_hash=password_hash,
        role="PERSONNEL"
    )
    db.add(personnel_demo)
    
    db.commit()
    
    # 50 Fictional Personnel
    print("Generating 50 personnel...")
    personnel_list = [personnel_demo]
    for i in range(2, 51):
        p = User(
            organization_id=org.id,
            unit_id=random.choice(units).id,
            user_code=f"P{i:03d}",
            name=f"Fictional Personnel {i}",
            email=f"p{i:03d}@demo.com",
            password_hash=password_hash,
            role="PERSONNEL"
        )
        db.add(p)
        personnel_list.append(p)
        
    db.commit()
    
    # Generate 30 days of checkins
    print("Generating check-ins for 30 days...")
    today = datetime.now(timezone.utc).date()
    for p in personnel_list:
        for day_offset in range(30):
            checkin_date = today - timedelta(days=day_offset)
            
            # Skip some days randomly
            if random.random() < 0.1:
                continue
                
            checkin = WellnessCheckin(
                personnel_id=p.id,
                checkin_date=checkin_date,
                sleep_hours=random.uniform(4.0, 9.0),
                sleep_quality=random.randint(1, 5),
                mood_score=random.randint(1, 5),
                energy_score=random.randint(1, 5),
                workload_score=random.randint(1, 5),
                stress_score=random.randint(1, 5)
            )
            db.add(checkin)
            
    db.commit()
    
    print("Seeding complete!")
    db.close()

if __name__ == "__main__":
    seed()
