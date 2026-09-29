# 🏗️ ManRakshak AI — System Architecture

## Overview

ManRakshak AI is designed as a **microservice-style monorepo** with clearly separated concerns: a Python FastAPI backend, React/TypeScript frontends, a Flutter mobile app, and a standalone ML training engine. All services communicate via a REST API.

---

## 🗺️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │  Web Dashboard   │  │  Mobile Web App  │  │  Flutter Mobile  │  │
│  │  React 19 + TS   │  │  React + Vite    │  │  App (Android)   │  │
│  │  Port: 5173/8080 │  │  Port: 5174/8081 │  │  Direct Device   │  │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘  │
│           │                     │                      │            │
└───────────┼─────────────────────┼──────────────────────┼────────────┘
            │    HTTPS REST API   │                      │
            │    (JWT Bearer)     │                      │
            ▼                     ▼                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      FASTAPI BACKEND (Port 8000)                   │
│                                                                     │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │  Auth/RBAC  │  │  Rate Limiter │  │  Security Headers/CORS    │  │
│  │  JWT + bcrypt│  │  5 req/min   │  │  HSTS, nosniff, X-Frame   │  │
│  └──────┬──────┘  └──────────────┘  └───────────────────────────┘  │
│         │                                                           │
│  ┌──────▼──────────────────────────────────────────────────────┐   │
│  │                     API Router (v1)                         │   │
│  │  /auth  /personnel  /wellness  /support  /interventions     │   │
│  │  /analytics  /reports  /notifications  /admin  /ai          │   │
│  └──────┬──────────────────────────────────────────────────────┘   │
│         │                                                           │
│  ┌──────▼──────────────┐   ┌───────────────────────────────────┐   │
│  │   Business Logic    │   │          AI Gateway               │   │
│  │   Services Layer    │   │  ┌─────────────────────────────┐  │   │
│  │                     │   │  │  OpenRouter Provider        │  │   │
│  │  - WellnessService  │   │  │  Model: qwen3.8-27b:free    │  │   │
│  │  - RiskService      │◄──┤  │  AI Firewall (content safe) │  │   │
│  │  - InterventionSvc  │   │  │  Privacy Filter             │  │   │
│  │  - NotificationSvc  │   │  └─────────────────────────────┘  │   │
│  └──────┬──────────────┘   └───────────────────────────────────┘   │
│         │                                                           │
│  ┌──────▼──────────────────────────────────────────────────────┐   │
│  │               SQLAlchemy ORM Layer                          │   │
│  └──────┬──────────────────────────────────────────────────────┘   │
│         │                                                           │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────┐   ┌──────────────────────────────────────────┐
│   PostgreSQL DB     │   │         ML Inference Layer               │
│   (Port 5432/5433)  │   │                                          │
│                     │   │  ┌──────────────────────────────────┐   │
│  - Users/Auth       │   │  │  XGBoost Classifier              │   │
│  - Personnel        │   │  │  (calibrated_xgboost.pkl)        │   │
│  - Wellness Data    │   │  │                                  │   │
│  - Interventions    │   │  │  SHAP TreeExplainer              │   │
│  - Audit Logs       │   │  │  (base_xgboost_for_shap.pkl)     │   │
│  - Notifications    │   │  │                                  │   │
└─────────────────────┘   │  Features (13):                    │   │
                          │  sleep_hours, mood_score,          │   │
                          │  workload_perception, night_duty,  │   │
                          │  sleep/mood/workload deviations,   │   │
                          │  deployment_duration, etc.         │   │
                          └──────────────────────────────────────┘   
```

---

## 🔄 Data Flow

### 1. Personnel Daily Check-In Flow

```
Personnel (Mobile App)
    │
    ▼  POST /api/v1/wellness/checkins
FastAPI Backend
    │
    ├─► Validate JWT token & RBAC
    ├─► Store check-in in PostgreSQL
    ├─► Load XGBoost model → predict risk score
    ├─► Run SHAP → extract top-3 contributing factors
    ├─► If risk ≥ 0.5 → trigger notification to Welfare Officer
    └─► Return risk assessment to client
```

### 2. AI Chat Flow

```
User (any role)
    │
    ▼  POST /api/v1/ai/chat
FastAPI Backend
    │
    ├─► Validate JWT + RBAC
    ├─► AI Firewall → reject harmful prompts
    ├─► Privacy Filter → strip PII from context
    ├─► AI Gateway → OpenRouter Provider
    │       └─► Qwen 3.8-27B (qwen/qwen3.8-27b:free)
    └─► Return sanitized response
```

### 3. Analytics Flow (K-Anonymity)

```
Commander / Welfare Officer
    │
    ▼  GET /api/v1/analytics/unit-summary
FastAPI Backend
    │
    ├─► Verify role ≥ Commander
    ├─► Query PostgreSQL (aggregate stats, never raw individual data)
    ├─► Privacy Check: cohort size ≥ 5 (ANALYTICS_MIN_COHORT_SIZE)
    └─► Return anonymized statistics
```

---

## 🧩 Component Responsibilities

### Backend (`/backend`)

| Module | Responsibility |
|---|---|
| `app/api/v1/` | HTTP route handlers — parse requests, delegate to services |
| `app/services/` | Business logic — orchestrates DB + AI + notifications |
| `app/models/` | SQLAlchemy ORM database models |
| `app/schemas/` | Pydantic validation for request/response bodies |
| `app/core/config.py` | Centralized settings via pydantic-settings |
| `app/core/database.py` | DB session factory |
| `app/core/security.py` | JWT creation/verification, bcrypt hashing |
| `app/ai/gateway.py` | Provider factory — decouples AI provider from business logic |
| `app/ai/firewall.py` | LLM prompt safety filter |
| `app/ai/features.py` | Feature engineering for ML inference |
| `app/security/authorization.py` | RBAC permission checks |
| `app/security/privacy_policy.py` | Data access privacy rules |

### Web Dashboard (`/web_dashboard`)

| Module | Responsibility |
|---|---|
| `src/features/` | Feature modules (wellness, reports, interventions, admin) |
| `src/components/` | Reusable UI components (charts, cards, tables) |
| `src/contexts/` | React context (auth state, theme) |
| `src/layouts/` | Page layout wrappers (sidebar, header) |

### Mobile App (`/mobile_app`)

| Module | Responsibility |
|---|---|
| `lib/screens/` | App screens (login, dashboard, check-in, support) |
| `lib/services/` | HTTP service layer (calls backend API) |
| `lib/models/` | Dart data models |
| `lib/providers/` | State management (Provider pattern) |

### AI Engine (`/ai_engine`)

| Module | Responsibility |
|---|---|
| `model.py` | Training pipeline: data loading → feature engineering → XGBoost → SHAP → export |
| `models/` | Trained `.pkl` artifact files loaded by backend at runtime |

---

## 🔐 Security Architecture

### Authentication Flow

```
Client                   Backend                    DB
  │                         │                        │
  │── POST /auth/login ────►│                        │
  │   {username, password}  │── bcrypt.verify() ────►│
  │                         │◄── User record ─────── │
  │                         │                        │
  │                         │── generate JWT ─────►  │
  │                         │   (access: 24h)        │
  │                         │   (refresh: 7d)        │
  │◄── {access_token,       │                        │
  │     refresh_token} ─────│                        │
  │                         │                        │
  │── GET /api/v1/... ──────►│                        │
  │   Authorization: Bearer │── decode JWT ─────────►│
  │                         │── check role ──────────│
  │◄── 200 OK ──────────────│                        │
```

### RBAC Hierarchy

```
Admin
  └── Welfare Officer
        └── Commander
              └── Personnel (lowest access)
```

- Personnel can only see their OWN data
- Commanders see unit-level aggregated (anonymized) data
- Welfare Officers see individual data within their assigned units
- Admins have full system access

---

## 🐳 Docker Deployment Architecture

```
docker-compose.yml
├── db (postgres:15)
│     Port: 5433:5432
│     Volume: postgres_data:/var/lib/postgresql/data
│
├── backend (python:3.11-slim)
│     Port: 8000:8000
│     Depends: db
│     Env: DATABASE_URL (uses db service name)
│
├── web_dashboard (nginx:alpine)
│     Port: 8080:80
│     Depends: backend
│     Nginx serves React build
│
└── mobile_web_app (nginx:alpine)
      Port: 8081:80
      Depends: backend
      Nginx serves React build
```

---

## 📊 Database Architecture

See [DATABASE.md](./DATABASE.md) for full schema.

**Core Tables:**
- `users` — Authentication + profile
- `personnel` — Police personnel records
- `wellness_checkins` — Daily wellness entries
- `interventions` — Assigned interventions
- `support_requests` — Personnel support tickets
- `notifications` — System notifications
- `audit_logs` — Immutable audit trail
- `organizations` / `units` — Organizational hierarchy

---

## 🔮 AI Architecture

See [AI_ENGINE.md](./AI_ENGINE.md) for full documentation.

**Inference Pipeline:**
1. Feature extraction from wellness check-in data
2. Temporal feature engineering (7-day rolling baselines, deviations)
3. XGBoost calibrated classification → risk probability [0,1]
4. SHAP TreeExplainer → top-3 human-readable risk factors
5. Risk category: `Normal` (< 0.5) or `Elevated` (≥ 0.5)
