# 🔐 ManRakshak AI — Authentication & Authorization Documentation

## Overview

ManRakshak uses a **JWT (JSON Web Token)** based authentication system with:
- **Access tokens** (short-lived: 24 hours)
- **Refresh tokens** (long-lived: 7 days, stored in DB)
- **RBAC** (Role-Based Access Control) with 4 roles
- **bcrypt** password hashing
- **Rate limiting** on login (5 attempts/minute)

---

## 👥 User Roles

| Role | Level | Capabilities |
|---|---|---|
| `personnel` | 1 (lowest) | Submit own check-ins, view own data, create support requests |
| `commander` | 2 | View anonymized unit dashboard and notifications |
| `welfare_officer` | 3 | Full wellness data, create interventions, view reports, AI predictions |
| `admin` | 4 (highest) | Full system access, user management, system settings |

### Permission Matrix

| Endpoint | Personnel | Commander | Welfare Officer | Admin |
|---|:---:|:---:|:---:|:---:|
| Submit check-in | ✅ | ❌ | ❌ | ✅ |
| View own data | ✅ | ✅ | ✅ | ✅ |
| View others' data | ❌ | 👁️ anon | ✅ | ✅ |
| Create intervention | ❌ | ❌ | ✅ | ✅ |
| View analytics | ❌ | ✅ anon | ✅ full | ✅ |
| Generate reports | ❌ | ❌ | ✅ | ✅ |
| AI predictions | ❌ | ❌ | ✅ | ✅ |
| Manage users | ❌ | ❌ | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ❌ | ✅ |

> 👁️ anon = anonymized/aggregated data only

---

## 🔑 JWT Token Structure

### Access Token Payload

```json
{
  "sub": "user_id_here",
  "role": "welfare_officer",
  "organization_id": "org_uuid",
  "exp": 1234567890,
  "iat": 1234567890,
  "type": "access"
}
```

### Refresh Token Payload

```json
{
  "sub": "user_id_here",
  "type": "refresh",
  "exp": 1234567890
}
```

Refresh tokens are also stored in the database to allow server-side revocation.

---

## 🔄 Authentication Flow

### 1. Login

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "officer123",
  "password": "SecurePass@1234"
}
```

**Success Response (200)**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "officer123",
    "role": "welfare_officer",
    "organization_id": "uuid"
  }
}
```

**Error Responses**:
```json
// 401 — wrong password or username
{"detail": "Invalid credentials"}

// 429 — too many attempts
{"detail": "Too many login attempts. Try again in 60 seconds."}
```

### 2. Authenticated Requests

Include the access token in every request:

```bash
curl http://localhost:8000/api/v1/wellness/checkins \
  -H "Authorization: Bearer eyJhbGc..."
```

### 3. Token Refresh

When the access token expires (401 response), use the refresh token:

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}
```

**Success Response (200)**:
```json
{
  "access_token": "eyJhbGc...(new token)...",
  "token_type": "bearer"
}
```

### 4. Logout

```
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGc...

{
  "refresh_token": "eyJhbGc..."
}
```

This revokes the refresh token from the database (server-side invalidation).

---

## 🛡️ Password Security

### Password Hashing

```python
# Hashing (at registration)
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("user_password")

# Verification (at login)
is_valid = pwd_context.verify("user_password", hashed)
```

### Password Requirements

- Minimum 8 characters
- Validated via Pydantic schema

---

## 🚦 Rate Limiting

Login endpoint is rate-limited to prevent brute force:

```python
# Configuration in backend/.env
RATE_LIMIT_LOGIN=5  # requests per minute per IP
```

Implementation uses in-memory sliding window counter (`app/api/rate_limiter.py`).

---

## 📋 Registration

### Register a New User (Admin only in production)

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "constable456",
  "email": "constable@police.gov.in",
  "password": "SecurePass@1234",
  "role": "personnel",
  "organization_id": "uuid-here"
}
```

**Success Response (201)**:
```json
{
  "id": "uuid",
  "username": "constable456",
  "role": "personnel",
  "organization_id": "uuid",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

## 🔒 Organization Scope

All data is **organization-scoped** — users can only access data within their own organization:

```python
# In app/security/organization_scope.py
def check_org_access(current_user: User, resource_org_id: UUID) -> bool:
    if current_user.role == "admin":
        return True
    return current_user.organization_id == resource_org_id
```

Welfare Officers can access data for all units within their organization.  
Commanders can access anonymized data for their assigned unit only.  
Personnel can only access their own data.

---

## 🔍 RBAC Implementation

### Dependency Injection Pattern

```python
# app/api/deps.py
from fastapi import Depends, HTTPException
from app.core.security import verify_access_token

async def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    payload = verify_access_token(token)
    user = db.query(User).filter(User.id == payload["sub"]).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles: str):
    """Factory for role-specific dependency."""
    async def _check(current_user = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return _check
```

### Usage in Route Handlers

```python
# app/api/v1/interventions.py
from app.api.deps import require_role

@router.post("/")
async def create_intervention(
    data: InterventionCreate,
    current_user = Depends(require_role("welfare_officer", "admin")),
    db = Depends(get_db)
):
    ...
```

---

## 🔐 Security Headers

Applied to every response by the `SecurityHeadersMiddleware`:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Request-ID: <uuid>  ← for request tracing
```

---

## 🔑 Generating a JWT Secret

```powershell
# PowerShell
python -c "import secrets; print(secrets.token_hex(32))"

# Example output:
# a3f8c2e1d94b7f6a8c2e1d94b7f6a8c2e1d94b7f6a8c2e1d94b7f6a8c2e1d94b
```

Minimum recommended: 32 bytes (64 hex characters).

---

## 🖥️ Frontend Authentication

### Web Dashboard (React)

The `AuthContext` manages token lifecycle:

```typescript
// contexts/AuthContext.tsx
const login = async (username: string, password: string) => {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    body: JSON.stringify({ username, password }),
    headers: { 'Content-Type': 'application/json' }
  });
  const data = await res.json();
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('refresh_token', data.refresh_token);
};
```

### Flutter App (Secure Storage)

```dart
// services/api_service.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final _storage = FlutterSecureStorage();

// Store tokens securely (Android Keystore / iOS Keychain)
await _storage.write(key: 'access_token', value: token);

// Retrieve token
final token = await _storage.read(key: 'access_token');

// Include in requests
headers: {'Authorization': 'Bearer $token'}
```

---

## 🕵️ Audit Logging

All sensitive operations (login, data access, changes) are logged to the `audit_logs` table:

```json
{
  "id": "uuid",
  "user_id": "uuid",
  "action": "WELLNESS_DATA_ACCESSED",
  "resource": "personnel/uuid",
  "timestamp": "2024-01-15T10:30:00Z",
  "ip_address": "192.168.1.1",
  "details": {}
}
```

Audit logs are **immutable** and only accessible by Admins.
