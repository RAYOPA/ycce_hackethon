# 🗃️ ManRakshak AI — Database Documentation

## Overview

ManRakshak uses **PostgreSQL 15** in production and **SQLite** for local development. The database is managed via **SQLAlchemy 2.0 ORM** and **Alembic** for schema migrations.

---

## 🔧 Database Configuration

### Connection Strings

```bash
# PostgreSQL (production / Docker)
DATABASE_URL=postgresql://postgres:password@localhost:5432/manrakshak

# PostgreSQL (Docker internal — uses service name)
DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak

# SQLite (local development — no setup needed)
DATABASE_URL=sqlite:///./manrakshak.db
```

### SQLAlchemy Setup (`app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

---

## 📊 Database Schema

### Entity Relationship Overview

```
organizations (1) ──── (N) units
                              │
                              └── (N) users
                                        │
                              ┌─────────┼─────────────┐
                              │         │             │
                    wellness_checkins  support_    interventions
                              │       requests
                              │
                         [AI Risk Score
                          Stored here]

users ──── (N) audit_logs
users ──── (N) notifications
users ──── (N) refresh_tokens
```

---

## 📋 Table Definitions

### `users`

The core authentication and profile table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Unique user identifier |
| `username` | VARCHAR(50) | UNIQUE, NOT NULL | Login username |
| `email` | VARCHAR(255) | UNIQUE | Email address |
| `hashed_password` | VARCHAR(255) | NOT NULL | bcrypt hash |
| `role` | ENUM | NOT NULL | `personnel`, `commander`, `welfare_officer`, `admin` |
| `organization_id` | UUID | FK → organizations | Parent organization |
| `unit_id` | UUID | FK → units | Assigned unit (for personnel) |
| `is_active` | BOOLEAN | DEFAULT TRUE | Account enabled flag |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Account creation time |
| `updated_at` | TIMESTAMP | AUTO UPDATE | Last modification |

---

### `organizations`

Top-level organizational hierarchy (e.g., Police District HQ).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Organization ID |
| `name` | VARCHAR(255) | NOT NULL | Organization name |
| `code` | VARCHAR(50) | UNIQUE | Short code (e.g., "MH-PUNE") |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### `units`

Sub-units within an organization (e.g., Police Station, Company).

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Unit ID |
| `name` | VARCHAR(255) | NOT NULL | Unit name |
| `organization_id` | UUID | FK → organizations | Parent org |
| `commander_id` | UUID | FK → users | Assigned commander |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### `wellness_checkins`

Daily wellness submissions from personnel. This is the core data table.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Check-in ID |
| `personnel_id` | UUID | FK → users, NOT NULL | Who submitted |
| `date` | DATE | NOT NULL | Check-in date |
| `sleep_hours` | FLOAT | NOT NULL | Hours slept (0-12) |
| `mood_score` | INTEGER | NOT NULL | Mood (1-10) |
| `workload_perception` | INTEGER | NOT NULL | Stress from workload (1-10) |
| `night_duty` | BOOLEAN | DEFAULT FALSE | Night shift flag |
| `deployment_duration_months` | INTEGER | | Months in current deployment |
| `duty_duration_hrs` | FLOAT | | Today's duty hours |
| `consecutive_duty_days` | INTEGER | | Consecutive days without off |
| `leave_gap_days` | INTEGER | | Days since last leave |
| `training_load` | INTEGER | | Training intensity (1-5) |
| `notes` | TEXT | | Optional free-text notes |
| `risk_score` | FLOAT | | AI-computed risk [0.0-1.0] |
| `risk_category` | VARCHAR(20) | | `Normal` or `Elevated` |
| `risk_factors` | JSON | | SHAP top factors |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Submission time |

**Indexes**:
- `(personnel_id, date)` — for historical queries
- `(date)` — for daily aggregate queries
- `risk_score` — for filtering high-risk personnel

---

### `interventions`

Interventions assigned to personnel by welfare officers.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Intervention ID |
| `personnel_id` | UUID | FK → users | Target personnel |
| `assigned_by` | UUID | FK → users | Welfare officer who assigned |
| `type` | ENUM | NOT NULL | `counseling`, `leave`, `reassignment`, `medical`, `peer_support` |
| `status` | ENUM | NOT NULL | `pending`, `in_progress`, `completed`, `cancelled` |
| `notes` | TEXT | | Details / instructions |
| `due_date` | DATE | | Target completion date |
| `completed_at` | TIMESTAMP | | Actual completion time |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### `support_requests`

Support requests submitted by personnel.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Request ID |
| `personnel_id` | UUID | FK → users | Requester |
| `type` | ENUM | NOT NULL | `mental_health`, `medical`, `family`, `legal`, `financial`, `other` |
| `urgency` | ENUM | NOT NULL | `low`, `medium`, `high`, `critical` |
| `description` | TEXT | NOT NULL | Request details |
| `status` | ENUM | NOT NULL | `open`, `in_review`, `resolved`, `closed` |
| `assigned_to` | UUID | FK → users | Welfare officer handling |
| `resolution_notes` | TEXT | | Resolution details |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |
| `updated_at` | TIMESTAMP | AUTO UPDATE | |

---

### `notifications`

System notifications for all user types.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Notification ID |
| `user_id` | UUID | FK → users | Recipient |
| `type` | VARCHAR(50) | NOT NULL | `risk_alert`, `intervention_assigned`, `support_update`, `system` |
| `title` | VARCHAR(255) | NOT NULL | Notification title |
| `message` | TEXT | NOT NULL | Full message |
| `is_read` | BOOLEAN | DEFAULT FALSE | Read status |
| `metadata` | JSON | | Additional context |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### `refresh_tokens`

Stored refresh tokens for server-side revocation.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Token ID |
| `user_id` | UUID | FK → users | Owner |
| `token_hash` | VARCHAR(255) | UNIQUE, NOT NULL | Hashed refresh token |
| `expires_at` | TIMESTAMP | NOT NULL | Expiration |
| `revoked` | BOOLEAN | DEFAULT FALSE | Revocation flag |
| `created_at` | TIMESTAMP | DEFAULT NOW() | |

---

### `audit_logs`

Immutable audit trail for all sensitive operations.

| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | UUID | PK | Log entry ID |
| `user_id` | UUID | FK → users | Actor |
| `action` | VARCHAR(100) | NOT NULL | Action code (e.g., `LOGIN`, `DATA_EXPORT`) |
| `resource_type` | VARCHAR(50) | | Resource type accessed |
| `resource_id` | UUID | | Resource ID |
| `ip_address` | INET | | Client IP |
| `details` | JSON | | Additional context |
| `created_at` | TIMESTAMP | DEFAULT NOW() | Immutable timestamp |

---

## 🔄 Alembic Migrations

### Setup

```bash
cd backend
.\venv\Scripts\Activate.ps1

# Initialize Alembic (already done — alembic.ini exists)
# alembic init migrations

# Apply migrations
alembic upgrade head
```

### Common Commands

```bash
# Apply all pending migrations (go to latest)
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Roll back one step
alembic downgrade -1

# Roll back to specific revision
alembic downgrade <revision_id>

# Roll back all migrations (empty DB)
alembic downgrade base

# Auto-generate migration from model changes
alembic revision --autogenerate -m "add_support_request_table"

# View migration history
alembic history --verbose

# View current applied version
alembic current

# Show pending migrations
alembic heads
```

### Creating a New Migration

1. Modify `app/models/*.py` to add/change models
2. Run: `alembic revision --autogenerate -m "describe your change"`
3. Review the generated file in `migrations/versions/`
4. Apply: `alembic upgrade head`

---

## 🐘 PostgreSQL Administration

### Docker Access

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U postgres -d manrakshak

# Useful psql commands:
\dt              -- List all tables
\d wellness_checkins  -- Describe table structure
\l               -- List databases
\q               -- Quit
```

### Direct Connection (Local PostgreSQL)

```bash
psql -U postgres -d manrakshak -h localhost -p 5432
```

### Database Backup

```bash
# Backup (Docker)
docker-compose exec db pg_dump -U postgres manrakshak > backup.sql

# Restore
docker-compose exec -T db psql -U postgres manrakshak < backup.sql
```

---

## 🔐 Data Privacy

### K-Anonymity for Analytics

Analytics queries enforce minimum cohort sizes:

```python
# ANALYTICS_MIN_COHORT_SIZE=5 in .env
# No aggregate is returned if fewer than 5 personnel are in the group
if cohort_count < settings.ANALYTICS_MIN_COHORT_SIZE:
    return {"error": "Insufficient data for privacy-preserving analytics"}
```

### Data Minimization

- Personnel daily check-ins only store wellness metrics, never location
- AI model features exclude personally identifiable fields
- LLM chat context strips PII before sending to OpenRouter

### Data Retention

Sensitive wellness data should be purged per policy (configurable via admin settings).

---

## 📈 Performance Indexes

Key indexes defined in SQLAlchemy models:

```python
# In models/wellness.py
__table_args__ = (
    Index("ix_wellness_personnel_date", "personnel_id", "date"),
    Index("ix_wellness_risk_score", "risk_score"),
)

# In models/audit.py
__table_args__ = (
    Index("ix_audit_user_id", "user_id"),
    Index("ix_audit_created_at", "created_at"),
)
```
