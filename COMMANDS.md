# 🚀 ManRakshak AI — Commands Reference

> **Complete reference for running, configuring, and deploying every component of the ManRakshak platform.**

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Backend API Server](#backend-api-server)
- [Web Dashboard](#web-dashboard)
- [Mobile Web App](#mobile-web-app)
- [Mobile App (Flutter)](#mobile-app-flutter)
- [AI Engine](#ai-engine)
- [Docker — Full Stack](#docker--full-stack)
- [Database Migrations](#database-migrations)
- [API URLs & Keys Reference](#api-urls--keys-reference)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Install these tools before running anything:

| Tool | Version | Download |
|---|---|---|
| Python | 3.11+ | https://python.org |
| Node.js | 18+ | https://nodejs.org |
| Flutter SDK | 3.x | https://flutter.dev |
| Docker + Compose | Latest | https://docker.com |
| Git | 2.x | https://git-scm.com |
| PostgreSQL | 15+ | https://postgresql.org (for local dev without Docker) |

---

## 🔐 Environment Setup

### Backend `.env` Configuration

```bash
# Copy the example file
cp backend/.env.example backend/.env
```

Edit `backend/.env` with your values:

```env
# ─── Database ──────────────────────────────────────────────────────────────
# For Docker: uses the postgres service name
DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak

# For local dev without Docker:
DATABASE_URL=sqlite:///./manrakshak.db
# OR PostgreSQL local:
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/manrakshak

# ─── Security (JWT) ────────────────────────────────────────────────────────
JWT_SECRET=your_super_secret_jwt_key_min_32_chars_long
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440     # 24 hours
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── CORS Origins ──────────────────────────────────────────────────────────
# Comma-separated list of allowed frontend origins
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,http://localhost:8080,http://localhost:8081

# ─── Analytics Privacy ─────────────────────────────────────────────────────
ANALYTICS_MIN_COHORT_SIZE=5          # K-anonymity minimum group size

# ─── Rate Limiting ─────────────────────────────────────────────────────────
RATE_LIMIT_LOGIN=5                   # Login attempts per minute

# ─── AI / LLM Gateway ──────────────────────────────────────────────────────
AI_PROVIDER=openrouter
OPEN_ROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxx  # Get from openrouter.ai
OPEN_ROUTER_MODEL=qwen/qwen3.8-27b:free
OPEN_ROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_REQUEST_TIMEOUT_SECONDS=30.0
```

> **🔑 Get your OpenRouter API key at:** https://openrouter.ai/keys  
> The free `qwen/qwen3.8-27b:free` model requires zero credits.

---

## 🐍 Backend API Server

### Local Development (SQLite — No Docker needed)

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (Windows CMD)
venv\Scripts\activate.bat

# Install dependencies
pip install -r requirements.txt

# Set environment for SQLite dev
# In backend/.env set: DATABASE_URL=sqlite:///./manrakshak.db

# Run database migrations
alembic upgrade head

# Start the server (development mode with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# OR use the provided batch script
..\start_backend.bat
```

### Production Start (Gunicorn)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Backend Service URLs

| Endpoint | URL | Description |
|---|---|---|
| **Root** | `http://localhost:8000/` | Health check |
| **Health** | `http://localhost:8000/health` | Server status |
| **OpenAPI Docs** | `http://localhost:8000/api/v1/openapi.json` | API Schema |
| **Swagger UI** | `http://localhost:8000/docs` | Interactive API browser |
| **ReDoc** | `http://localhost:8000/redoc` | Alternative API docs |

---

## 🌐 Web Dashboard

### Local Development

```powershell
# Navigate to web dashboard
cd web_dashboard

# Install dependencies
npm install

# Start development server (hot-reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Web Dashboard URL

| Environment | URL |
|---|---|
| Development | `http://localhost:5173` |
| Docker/Production | `http://localhost:8080` |

### Web Dashboard `.env`

Create `web_dashboard/.env.local`:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 📱 Mobile Web App

### Local Development

```powershell
# Navigate to mobile web app
cd mobile_web_app

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Mobile Web URL

| Environment | URL |
|---|---|
| Development | `http://localhost:5174` |
| Docker/Production | `http://localhost:8081` |

---

## 📲 Mobile App (Flutter)

### Setup Flutter App

```powershell
# Navigate to mobile app
cd mobile_app

# Get Flutter packages
flutter pub get

# Check connected devices
flutter devices

# Run on connected Android device
flutter run

# Run on Chrome browser (web)
flutter run -d chrome

# OR use the provided batch script
..\run_on_chrome.bat
..\run_on_phone.bat
```

### Configure API URL in Flutter App

Edit `mobile_app/lib/` — find the API configuration file and set:

```dart
const String kBaseUrl = 'http://YOUR_SERVER_IP:8000/api/v1';
// For local testing: http://10.0.2.2:8000/api/v1  (Android emulator)
// For physical device: http://192.168.X.X:8000/api/v1  (your local IP)
// For production: https://your-domain.com/api/v1
```

### Build APK

```powershell
# Build debug APK
flutter build apk --debug

# Build release APK
flutter build apk --release

# OR use the batch script
..\build_apk.bat

# Install to connected device
flutter install

# OR use the batch script
..\install_to_phone.bat
```

### Flutter App API Key Setup

The Flutter app uses `flutter_secure_storage` for secure token storage. The JWT token is obtained from the backend on login and stored securely — no manual API key configuration needed.

---

## 🤖 AI Engine

### Train the XGBoost Model

```powershell
# Navigate to ai_engine directory
cd ai_engine

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install xgboost shap scikit-learn pandas joblib

# Generate synthetic training data first (if not present)
cd ..\data_generation
python generate_data.py

# Train the model
cd ..\ai_engine
python model.py

# Trained models are saved to: ai_engine/models/
#   ├── calibrated_xgboost.pkl      (main prediction model)
#   ├── base_xgboost_for_shap.pkl   (for SHAP explanations)
#   └── feature_names.pkl           (feature order)
```

### Generate Synthetic Data

```powershell
cd data_generation
python generate_data.py
# Creates: synthetic_welfare_data.csv (in root directory)
```

### Verify AI System is Running (via API)

```bash
# Check AI health through the backend
curl http://localhost:8000/api/v1/ai/health

# Test AI risk prediction (requires auth token)
curl -X POST http://localhost:8000/api/v1/ai/predict \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"personnel_id": 1}'
```

---

## 🐳 Docker — Full Stack

### Start All Services

```bash
# Start all services in background
docker-compose up -d

# Start and view logs
docker-compose up

# Start specific service
docker-compose up backend -d
docker-compose up web_dashboard -d
```

### Service URLs (Docker)

| Service | Container Port | Host URL |
|---|---|---|
| **Backend API** | 8000 | `http://localhost:8000` |
| **Web Dashboard** | 80 → 8080 | `http://localhost:8080` |
| **Mobile Web App** | 80 → 8081 | `http://localhost:8081` |
| **PostgreSQL** | 5432 → 5433 | `localhost:5433` |

### Docker Management

```bash
# View running containers
docker-compose ps

# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f web_dashboard

# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes DB data)
docker-compose down -v

# Rebuild images after code changes
docker-compose build
docker-compose up -d --build

# Rebuild specific service
docker-compose build backend
docker-compose up -d backend
```

### Run Migrations Inside Docker

```bash
docker-compose exec backend alembic upgrade head
```

### Access PostgreSQL in Docker

```bash
# Connect to PostgreSQL container
docker-compose exec db psql -U postgres -d manrakshak
```

---

## 🗃️ Database Migrations

### Alembic Commands (Backend)

```bash
# Navigate to backend
cd backend

# Activate virtualenv
.\venv\Scripts\Activate.ps1

# Apply all pending migrations
alembic upgrade head

# Roll back last migration
alembic downgrade -1

# Roll back all migrations
alembic downgrade base

# Create a new migration (auto-detect model changes)
alembic revision --autogenerate -m "description of change"

# View migration history
alembic history

# View current migration version
alembic current
```

---

## 📡 API URLs & Keys Reference

### Complete API Endpoint Map

**Base URL**: `http://localhost:8000/api/v1`

#### Authentication Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register new user |
| `POST` | `/auth/login` | Login (returns JWT access + refresh tokens) |
| `POST` | `/auth/refresh` | Refresh access token |
| `POST` | `/auth/logout` | Logout (invalidate refresh token) |
| `GET` | `/auth/me` | Get current user profile |

#### Personnel Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/personnel/` | List all personnel (RBAC restricted) |
| `GET` | `/personnel/{id}` | Get personnel detail |
| `PUT` | `/personnel/{id}` | Update personnel info |

#### Wellness Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/wellness/checkins` | Submit daily wellness check-in |
| `GET` | `/wellness/checkins` | Get wellness check-in history |
| `GET` | `/wellness/risk/{personnel_id}` | Get AI risk assessment |

#### Support Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/support/requests` | Create support request |
| `GET` | `/support/requests` | List support requests |
| `PUT` | `/support/requests/{id}` | Update support request status |

#### Interventions Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/interventions/` | Create intervention |
| `GET` | `/interventions/` | List interventions |
| `PUT` | `/interventions/{id}` | Update intervention |

#### Analytics Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/analytics/unit-summary` | Unit-level anonymized wellness stats |
| `GET` | `/analytics/trends` | Trend data for charts |
| `GET` | `/analytics/risk-distribution` | Risk category distribution |

#### AI Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ai/chat` | AI wellness assistant chat |
| `POST` | `/ai/predict` | Get AI risk prediction |
| `GET` | `/ai/health` | AI service health check |

#### Admin Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/admin/users` | List all system users |
| `POST` | `/admin/users` | Create user account |
| `DELETE` | `/admin/users/{id}` | Delete user account |
| `GET` | `/admin/audit-logs` | View audit logs |

#### Reports Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/reports/wellness` | Generate wellness report |
| `GET` | `/reports/interventions` | Intervention activity report |

### External API Keys

| Service | Environment Variable | Obtain From |
|---|---|---|
| **OpenRouter (LLM)** | `OPEN_ROUTER_API_KEY` | https://openrouter.ai/keys |
| **PostgreSQL** | `DATABASE_URL` | Local or hosted PostgreSQL |
| **JWT Secret** | `JWT_SECRET` | Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |

### Generate JWT Secret

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Activate venv
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_auth.py -v

# Run tests with coverage report
pytest --cov=app --cov-report=html
```

### API Quick Test (cURL)

```bash
# 1. Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234","role":"personnel"}'

# 2. Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"Test@1234"}'

# 3. Use the token (replace TOKEN)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"

# 4. Check AI service
curl http://localhost:8000/api/v1/ai/health \
  -H "Authorization: Bearer TOKEN"
```

---

## 🌍 Public Access via Cloudflare Tunnel

For exposing the backend publicly (demos, mobile device testing):

```powershell
# Start backend first
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal — start Cloudflare tunnel
..\start_live_backend.bat
# OR manually:
cloudflared.exe tunnel --url http://localhost:8000
```

This generates a public HTTPS URL like: `https://xxxx.trycloudflare.com`  
Update the Flutter app's `kBaseUrl` to this URL for mobile testing over the internet.

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Check .env file exists
ls backend/.env

# Verify database connection
cd backend && python -c "from app.core.database import engine; print('DB OK')"
```

### AI service returns 503

```bash
# Verify OPEN_ROUTER_API_KEY is set in backend/.env
# Test OpenRouter directly:
curl https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer YOUR_KEY"
```

### Flutter app can't connect to backend

```bash
# For Android emulator — use 10.0.2.2 instead of localhost
# For physical device — use your machine's LAN IP
ipconfig | findstr IPv4
# Update kBaseUrl in Flutter app to: http://192.168.X.X:8000/api/v1
```

### Docker PostgreSQL connection refused

```bash
# Verify db container is running
docker-compose ps

# Check backend is using correct host (db, not localhost)
# DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak
#                                              ^^--- container service name
```
