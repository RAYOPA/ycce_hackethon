import pytest
from fastapi import APIRouter, Depends
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.models import User, Organization, Unit
from app.models.enums import UserRole, UserStatus
from app.core.security import get_password_hash
from app.api.deps import require_personnel, require_welfare_officer, require_commander, require_admin
from tests.conftest import TestingSessionLocal

rbac_test_router = APIRouter()
rbac_test_router.__test__ = False

@rbac_test_router.get("/personnel-only")
def p_only(user: User = Depends(require_personnel)):
    return {"status": "ok"}

@rbac_test_router.get("/welfare-only")
def w_only(user: User = Depends(require_welfare_officer)):
    return {"status": "ok"}

@rbac_test_router.get("/commander-only")
def c_only(user: User = Depends(require_commander)):
    return {"status": "ok"}

@rbac_test_router.get("/admin-only")
def a_only(user: User = Depends(require_admin)):
    return {"status": "ok"}

# Include only once
try:
    app.include_router(rbac_test_router, prefix="/test-rbac")
except Exception:
    pass

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_users():
    db = TestingSessionLocal()
    
    org = Organization(organization_code="RBAC_ORG", name="RBAC Test Org")
    db.add(org)
    db.commit()
    
    unit = Unit(organization_id=org.id, unit_code="RBAC_UNIT", unit_name="RBAC Unit")
    db.add(unit)
    db.commit()
    
    roles = [UserRole.PERSONNEL, UserRole.WELFARE_OFFICER, UserRole.COMMANDER, UserRole.ADMINISTRATOR]
    
    for idx, role in enumerate(roles):
        u = User(
            organization_id=org.id,
            unit_id=unit.id,
            user_code=f"RBAC_0{idx}",
            name=f"{role.value} User",
            email=f"{role.value.lower()}@example.com",
            password_hash=get_password_hash("password123"),
            role=role,
            status=UserStatus.ACTIVE
        )
        db.add(u)
        
    db.commit()
    
    yield db
    db.close()

def get_token_for(email: str):
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        json={"email": email, "password": "password123"}
    )
    return response.json()["access_token"]

def test_personnel_access(setup_users):
    token = get_token_for("personnel@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.get("/test-rbac/personnel-only", headers=headers).status_code == 200
    assert client.get("/test-rbac/welfare-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/commander-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/admin-only", headers=headers).status_code == 403

def test_welfare_officer_access(setup_users):
    token = get_token_for("welfare_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.get("/test-rbac/personnel-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/welfare-only", headers=headers).status_code == 200
    assert client.get("/test-rbac/commander-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/admin-only", headers=headers).status_code == 403

def test_commander_access(setup_users):
    token = get_token_for("commander@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.get("/test-rbac/personnel-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/welfare-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/commander-only", headers=headers).status_code == 200
    assert client.get("/test-rbac/admin-only", headers=headers).status_code == 403

def test_admin_access(setup_users):
    token = get_token_for("administrator@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    assert client.get("/test-rbac/personnel-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/welfare-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/commander-only", headers=headers).status_code == 403
    assert client.get("/test-rbac/admin-only", headers=headers).status_code == 200

def test_organization_isolation(setup_users):
    from app.security.organization_scope import OrganizationScope
    from fastapi import HTTPException
    
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "personnel@example.com").first()
    
    # Same organization should not raise
    OrganizationScope.assert_same_organization(user, user.organization_id)
    
    # Different organization should raise 403
    import uuid
    fake_org_id = str(uuid.uuid4())
    with pytest.raises(HTTPException) as exc_info:
        OrganizationScope.assert_same_organization(user, fake_org_id)
        
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Security violation: Cross-organization access is strictly forbidden."
    db.close()
