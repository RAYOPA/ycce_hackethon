import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from app.core.database import SessionLocal, Base, engine
from datetime import date

# Set up test database
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()
org_a = Organization(organization_code="ORG_A", name="Command Alpha")
org_b = Organization(organization_code="ORG_B", name="Command Bravo")
db.add_all([org_a, org_b])
db.commit()

unit_a = Unit(organization_id=org_a.id, unit_code="UNIT_A", unit_name="Alpha Unit")
unit_b = Unit(organization_id=org_b.id, unit_code="UNIT_B", unit_name="Bravo Unit")
db.add_all([unit_a, unit_b])
db.commit()

users = [
    User(organization_id=org_a.id, unit_id=unit_a.id, user_code="P_A1", name="Personnel A1", email="pa1@example.com", password_hash=get_password_hash("pass"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE),
    User(organization_id=org_a.id, unit_id=unit_a.id, user_code="P_A2", name="Personnel A2", email="pa2@example.com", password_hash=get_password_hash("pass"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE),
    User(organization_id=org_a.id, unit_id=unit_a.id, user_code="W_A1", name="Welfare A1", email="wa1@example.com", password_hash=get_password_hash("pass"), role=UserRole.WELFARE_OFFICER, status=UserStatus.ACTIVE),
    User(organization_id=org_a.id, unit_id=unit_a.id, user_code="C_A1", name="Commander A1", email="ca1@example.com", password_hash=get_password_hash("pass"), role=UserRole.COMMANDER, status=UserStatus.ACTIVE),
    User(organization_id=org_a.id, unit_id=unit_a.id, user_code="ADM_A1", name="Admin A1", email="adma1@example.com", password_hash=get_password_hash("pass"), role=UserRole.ADMINISTRATOR, status=UserStatus.ACTIVE),
    User(organization_id=org_b.id, unit_id=unit_b.id, user_code="P_B1", name="Personnel B1", email="pb1@example.com", password_hash=get_password_hash("pass"), role=UserRole.PERSONNEL, status=UserStatus.ACTIVE)
]
db.add_all(users)
db.commit()

# Grab IDs
p_a1_id = db.query(User).filter_by(email="pa1@example.com").first().id
p_b1_id = db.query(User).filter_by(email="pb1@example.com").first().id
db.close()

client = TestClient(app)

def login(email):
    res = client.post(f"{settings.API_V1_STR}/auth/login", json={"email": email, "password": "pass"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

print("\n--- RUNNING V1 WORKFLOW VERIFICATION ---\n")

def check(name, condition):
    if condition:
        print(f"[PASS] {name}")
    else:
        print(f"[FAIL] {name}")

# --- Personnel Workflow ---
print("[PERSONNEL WORKFLOW]")
h_pa1 = login("pa1@example.com")
check("Personnel -> Login", h_pa1 is not None)

# Check-in
res_checkin = client.post(f"{settings.API_V1_STR}/wellness/checkins", json={
    "checkin_date": str(date.today()), "sleep_hours": 6, "sleep_quality": 3,
    "mood_score": 3, "energy_score": 3, "workload_score": 4, "stress_score": 4
}, headers=h_pa1)
check("Personnel -> Wellness check-in", res_checkin.status_code == 201)

# History
res_hist = client.get(f"{settings.API_V1_STR}/wellness/me", headers=h_pa1)
check("Personnel -> Wellness history", res_hist.status_code == 200)

# Support
res_supp = client.post(f"{settings.API_V1_STR}/support/requests", json={
    "request_type": "WORKLOAD", "message": "Too much workload"
}, headers=h_pa1)
check("Personnel -> Support request", res_supp.status_code == 201)

# Notifications
res_notif = client.get(f"{settings.API_V1_STR}/notifications", headers=h_pa1)
check("Personnel -> Notifications", res_notif.status_code == 200)

print("")
# --- Welfare Officer Workflow ---
print("[WELFARE OFFICER WORKFLOW]")
h_wa1 = login("wa1@example.com")
check("Welfare Officer -> Login", h_wa1 is not None)

res_pers = client.get(f"{settings.API_V1_STR}/personnel", headers=h_wa1)
check("Welfare Officer -> View authorized personnel", res_pers.status_code == 200)

res_w_hist = client.get(f"{settings.API_V1_STR}/wellness/{p_a1_id}", headers=h_wa1)
check("Welfare Officer -> View permitted wellness history", res_w_hist.status_code == 200)

res_supp_list = client.get(f"{settings.API_V1_STR}/support/requests", headers=h_wa1)
check("Welfare Officer -> Review support requests", res_supp_list.status_code == 200)
req_id = res_supp_list.json()["items"][0]["id"]

res_intv = client.post(f"{settings.API_V1_STR}/interventions", json={
    "personnel_id": p_a1_id, "action_type": "WELLNESS_FOLLOWUP", "notes": "Checking in", "follow_up_date": "2026-09-02T10:00:00Z"
}, headers=h_wa1)
check("Welfare Officer -> Create intervention & Schedule follow-up", res_intv.status_code == 201)

res_an_w = client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=h_wa1)
check("Welfare Officer -> View analytics", res_an_w.status_code == 200)

print("")
# --- Commander Workflow ---
print("[COMMANDER WORKFLOW]")
h_ca1 = login("ca1@example.com")
check("Commander -> Login", h_ca1 is not None)

res_an_w2 = client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=h_ca1)
check("Commander -> Aggregate wellness analytics", res_an_w2.status_code == 200)

res_rep = client.get(f"{settings.API_V1_STR}/reports/wellness/export?format=csv", headers=h_ca1)
check("Commander -> Reports / Export", res_rep.status_code == 200)

print("")
# --- Critical Privacy Firewalls ---
print("[CRITICAL PRIVACY FIREWALLS]")

res_c_well = client.get(f"{settings.API_V1_STR}/wellness/{p_a1_id}", headers=h_ca1)
check("Commander -X-> Individual Wellness", res_c_well.status_code == 403)

res_c_sup = client.get(f"{settings.API_V1_STR}/support/requests", headers=h_ca1)
check("Commander -X-> Private Support Request", res_c_sup.status_code == 403)

res_c_intv = client.get(f"{settings.API_V1_STR}/interventions", headers=h_ca1)
check("Commander -X-> Intervention Notes", res_c_intv.status_code == 403)

h_adma1 = login("adma1@example.com")
res_adm_well = client.get(f"{settings.API_V1_STR}/wellness/{p_a1_id}", headers=h_adma1)
check("Administrator -X-> Protected Welfare Data", res_adm_well.status_code == 403)

h_pa2 = login("pa2@example.com")
res_pa2_well = client.get(f"{settings.API_V1_STR}/wellness/{p_a1_id}", headers=h_pa2)
check("Personnel -X-> Other Personnel Data", res_pa2_well.status_code == 403)

res_pa2_an = client.get(f"{settings.API_V1_STR}/analytics/wellness", headers=h_pa2)
check("Personnel -X-> Organization Analytics", res_pa2_an.status_code == 403)

res_wa_orgb = client.get(f"{settings.API_V1_STR}/personnel/{p_b1_id}", headers=h_wa1)
check("Organization A -X-> Organization B", res_wa_orgb.status_code == 404)

print("\n--- VERIFICATION COMPLETE ---\n")
