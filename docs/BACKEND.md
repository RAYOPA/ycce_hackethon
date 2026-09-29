# 🐍 ManRakshak AI — Backend Documentation

## Overview

The ManRakshak backend is a **FastAPI** application built with Python 3.11. It serves as the central REST API for all client applications — web dashboard, mobile app, and mobile web app.

---

## 📁 Directory Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app instance, middleware, router registration
│   ├── ai/                  # AI/LLM integration layer
│   │   ├── __init__.py
│   │   ├── gateway.py       # AI provider factory (central entry point)
│   │   ├── interfaces.py    # Abstract AIProvider interface
│   │   ├── providers/       # Concrete provider implementations
│   │   │   └── openrouter.py
│   │   ├── firewall.py      # LLM prompt safety + content filtering
│   │   ├── privacy.py       # PII scrubbing for AI context
│   │   ├── features.py      # Feature engineering for ML inference
│   │   ├── baseline.py      # Personal baseline calculations
│   │   ├── data_access.py   # AI-specific DB queries
│   │   ├── schemas.py       # AI request/response Pydantic models
│   │   └── exceptions.py    # Custom AI error types
│   │
│   ├── api/
│   │   ├── deps.py          # FastAPI dependency injection (DB session, current user)
│   │   ├── rate_limiter.py  # In-memory rate limiting implementation
│   │   └── v1/              # API route handlers
│   │       ├── auth.py      # Login, register, refresh, logout
│   │       ├── personnel.py # Personnel CRUD
│   │       ├── wellness.py  # Check-ins, risk assessments
│   │       ├── support.py   # Support requests
│   │       ├── interventions.py
│   │       ├── notifications.py
│   │       ├── analytics.py # Anonymized unit statistics
│   │       ├── reports.py   # Report generation
│   │       ├── admin.py     # Admin user management
│   │       ├── privacy.py   # Privacy/data rights endpoints
│   │       └── ai.py        # AI chat + prediction endpoints
│   │
│   ├── core/
│   │   ├── config.py        # Application settings (pydantic-settings)
│   │   ├── database.py      # SQLAlchemy engine + session factory
│   │   └── security.py      # JWT utilities, bcrypt hashing
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── __init__.py      # Re-exports all models
│   │   ├── user.py          # User (auth + profile)
│   │   ├── auth.py          # RefreshToken model
│   │   ├── identity.py      # PersonnelIdentity
│   │   ├── wellness.py      # WellnessCheckin
│   │   ├── intervention.py  # Intervention
│   │   ├── support.py       # SupportRequest
│   │   ├── notification.py  # Notification
│   │   ├── audit.py         # AuditLog
│   │   ├── organization.py  # Organization
│   │   ├── unit.py          # Unit
│   │   ├── governance.py    # Governance policies
│   │   └── settings.py      # System settings
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── wellness.py
│   │   └── ...
│   │
│   ├── security/            # Authorization & privacy
│   │   ├── authorization.py      # Role permission checks
│   │   ├── organization_scope.py # Org-scoped data access
│   │   ├── privacy_policy.py     # Data access privacy rules
│   │   └── resource_access.py    # Resource-level access control
│   │
│   └── services/            # Business logic layer
│       └── ...
│
├── migrations/              # Alembic migration scripts
│   ├── env.py
│   └── versions/
│
├── tests/                   # Pytest test suites
├── docs/                    # Additional backend docs
├── scripts/                 # Utility scripts
│
├── .env                     # Runtime secrets (NOT committed)
├── .env.example             # Template for .env
├── alembic.ini              # Alembic configuration
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker build instructions
├── pytest.ini               # Test configuration
└── README.md
```

---

## ⚙️ Configuration

All settings are loaded from environment variables (via `backend/.env`) using `pydantic-settings`.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | *(required)* | PostgreSQL or SQLite connection string |
| `JWT_SECRET` | *(required)* | Secret for JWT signing (min 32 chars) |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | Access token TTL (24h) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token TTL |
| `CORS_ORIGINS` | `""` | Comma-separated allowed origins |
| `ANALYTICS_MIN_COHORT_SIZE` | `5` | K-anonymity minimum cohort |
| `RATE_LIMIT_LOGIN` | `5` | Login attempts per minute |
| `AI_PROVIDER` | `openrouter` | AI provider (`openrouter` or future providers) |
| `OPEN_ROUTER_API_KEY` | `""` | OpenRouter API key |
| `OPEN_ROUTER_MODEL` | `qwen/qwen3.8-27b:free` | LLM model identifier |
| `OPEN_ROUTER_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter endpoint |
| `AI_REQUEST_TIMEOUT_SECONDS` | `30.0` | AI request timeout |

---

## 🔒 Middleware Stack

The middleware executes in this order for every request:

1. **CORSMiddleware** — validates and handles cross-origin requests
2. **SecurityHeadersMiddleware** — adds `X-Content-Type-Options`, `X-Frame-Options`, `HSTS`, `X-Request-ID`
3. **RateLimiter** — per-IP rate limiting on `/auth/login`
4. **Route Handler** — actual request processing
5. **Exception Handlers** — global error normalization (SQLAlchemy, AI, generic)

---

## 🛣️ API Routes

**Base prefix**: `/api/v1`

### Auth (`/auth`)

```
POST /auth/register         — Create new account
POST /auth/login            — Returns {access_token, refresh_token}
POST /auth/refresh          — Exchange refresh token for new access token
POST /auth/logout           — Revoke refresh token
GET  /auth/me               — Get authenticated user's profile
PUT  /auth/me/password      — Change password
```

### Personnel (`/personnel`)

```
GET    /personnel/           — List personnel (Welfare Officer+)
GET    /personnel/{id}       — Get single personnel record
PUT    /personnel/{id}       — Update personnel info
DELETE /personnel/{id}       — Admin only
```

### Wellness (`/wellness`)

```
POST /wellness/checkins      — Submit daily check-in (Personnel)
GET  /wellness/checkins      — Get own check-in history
GET  /wellness/checkins/all  — Get all check-ins (Welfare Officer+)
GET  /wellness/risk/{id}     — AI risk assessment for personnel
```

### Interventions (`/interventions`)

```
POST /interventions/         — Create intervention (Welfare Officer+)
GET  /interventions/         — List interventions
GET  /interventions/{id}     — Get intervention detail
PUT  /interventions/{id}     — Update status/notes
```

### Analytics (`/analytics`)

```
GET /analytics/unit-summary     — Anonymized unit wellness stats (Commander+)
GET /analytics/trends           — Time-series trends
GET /analytics/risk-distribution — Risk category breakdown
```

### AI (`/ai`)

```
POST /ai/chat               — LLM chat with AI wellness assistant
POST /ai/predict            — XGBoost risk prediction (Welfare Officer+)
GET  /ai/health             — AI service availability check
```

### Admin (`/admin`)

```
GET    /admin/users          — List all users
POST   /admin/users          — Create user (Admin only)
PUT    /admin/users/{id}     — Update user
DELETE /admin/users/{id}     — Delete user
GET    /admin/audit-logs     — View audit trail
GET    /admin/system-settings — Get system configuration
```

---

## 🔑 Authentication

See [AUTHENTICATION.md](./AUTHENTICATION.md) for full details.

**Quick summary:**
- All non-auth routes require `Authorization: Bearer <access_token>` header
- Tokens are generated at login and refreshed via `/auth/refresh`
- JWT payload contains `user_id`, `role`, `organization_id`

---

## 🤖 AI Integration

The backend integrates AI at two levels:

### 1. XGBoost ML Inference (Internal)
- Model loaded at startup from `models/*.pkl`
- Called automatically when wellness check-ins are processed
- Returns `risk_probability`, `risk_category`, `top_factors` (SHAP)
- Located in `app/ai/features.py` and `app/services/`

### 2. LLM Chat (External via OpenRouter)
- Accessed via `/api/v1/ai/chat`
- Routes through `app/ai/gateway.py` → `app/ai/providers/openrouter.py`
- AI Firewall (`app/ai/firewall.py`) filters harmful content before sending
- Privacy filter strips PII from context before sending to LLM

---

## 📦 Dependencies

```
fastapi==0.110.0          # Web framework
uvicorn[standard]==0.29.0 # ASGI server
sqlalchemy==2.0.28        # ORM
psycopg2-binary>=2.9.9    # PostgreSQL adapter
alembic==1.13.1           # DB migrations
pydantic==2.6.3           # Data validation
pydantic-settings==2.2.1  # Settings management
email-validator>=2.1.0    # Email validation
bcrypt>=4.1.2,<5          # Password hashing
passlib[bcrypt]==1.7.4    # Password utilities
python-jose[cryptography] # JWT
python-multipart==0.0.9   # Form data parsing
httpx==0.27.0             # Async HTTP (for OpenRouter)
shap>=0.44.1              # ML explainability
xgboost>=2.0.3            # ML model
pandas>=2.2.0             # Data manipulation
joblib>=1.3.2             # Model serialization
scikit-learn>=1.4.0       # ML utilities
```

---

## 🧪 Testing

```bash
cd backend
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with verbose output + coverage
pytest -v --cov=app

# Run specific test categories
pytest tests/test_auth.py -v
pytest tests/test_wellness.py -v
pytest tests/test_ai.py -v
```

Test configuration is in `backend/pytest.ini`.

---

## 🐳 Docker Build

```dockerfile
FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y libpq-dev gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
