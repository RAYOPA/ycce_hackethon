# 🛡️ ManRakshak AI — Complete Project Documentation & Operations Guide

> **AI-Driven Comprehensive Welfare, Psychological Health & Fatigue Monitoring Platform for Defense and High-Stress Operational Forces.**

---

## 📑 Table of Contents

1. [System Architecture & Components](#-system-architecture--components)
2. [Currently Running Servers & Live URLs](#-currently-running-servers--live-urls)
3. [Pre-configured Demo Accounts & Credentials](#-pre-configured-demo-accounts--credentials)
4. [One-Click Quick Start Scripts](#-one-click-quick-start-scripts)
5. [Manual Step-by-Step Execution Guide](#-manual-step-by-step-execution-guide)
   - [Backend API Server (FastAPI)](#1-backend-api-server-fastapi)
   - [Commander & Admin Web Dashboard (React)](#2-commander--admin-web-dashboard-react)
   - [Personnel Mobile Web App (React PWA)](#3-personnel-mobile-web-app-react-pwa)
   - [Native Mobile App (Flutter / Android APK)](#4-native-mobile-app-flutter--android-apk)
   - [Docker Full-Stack Deployment](#5-docker-full-stack-deployment)
6. [Environment Variables & API Keys Reference](#-environment-variables--api-keys-reference)
   - [Backend `.env` Configuration](#backend-env-configuration)
   - [Frontend `.env` Configuration](#frontend-env-configuration)
   - [OpenRouter AI LLM Key Setup](#openrouter-ai-llm-key-setup)
7. [API Endpoints Reference (FastAPI v1)](#-api-endpoints-reference-fastapi-v1)
8. [Database Management & Seeding](#-database-management--seeding)
9. [Automated Testing & Validation](#-automated-testing--validation)
10. [Troubleshooting & FAQs](#-troubleshooting--faqs)

---

## 🏗️ System Architecture & Components

ManRakshak AI is built with an enterprise-grade modular architecture designed for operational resilience, end-to-end data privacy, and proactive AI analytics:

| Component | Technology | Directory | Default Port / URL |
|---|---|---|---|
| **Backend REST API** | FastAPI, SQLAlchemy, SQLite/PostgreSQL, Pydantic, Uvicorn | `/backend` | `http://127.0.0.1:8000` |
| **API Interactive Docs** | Swagger UI & OpenAPI 3.0 | `/backend` | `http://127.0.0.1:8000/docs` |
| **Web Dashboard** | React 18, Vite, TypeScript, Tailwind CSS, Lucide, Recharts | `/web_dashboard` | `http://localhost:5173` |
| **Mobile Web App** | React 18, Vite, TypeScript, Tailwind CSS, Responsive PWA | `/mobile_web_app` | `http://localhost:5174` |
| **Native Mobile App** | Flutter 3.x, Dart (Android APK & iOS) | `/mobile_app` | Run via Chrome or Android device |
| **AI Risk Engine** | OpenRouter LLM Gateway, ML Welfare Models, Anonymity Firewall | `/backend/app/ai` & `/ai_engine` | Embedded in Backend API |
| **Pre-built Android APK** | Standalone Compiled Android Application Package | Root `/` | `ManRakshak.apk` |

---

## 🟢 Currently Running Servers & Live URLs

The services are verified, tested, and actively running on your local machine:

- **FastAPI Backend Server:** [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- **Interactive Swagger Documentation:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **Alternative ReDoc Documentation:** [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)
- **Commander / Admin Web Dashboard:** [`http://localhost:5173`](http://localhost:5173)
- **Personnel Mobile Web Application:** [`http://localhost:5174`](http://localhost:5174)

---

## 👥 Pre-configured Demo Accounts & Credentials

The local database (`backend/manrakshak.db`) comes pre-seeded with real-world simulation data (50 personnel profiles, 30 days of daily wellness logs, risk metrics, and unit structures).

**Organization Code for all accounts:** `ORG001`  
**Default Password for all accounts:** `demo123`

| Role | Email / Identifier | Password | Access Scope |
|---|---|---|---|
| **Administrator** | `admin@demo.com` (Code: `A001`) | `demo123` | Full system settings, user management, audit logs, security policies |
| **Commander** | `commander@demo.com` (Code: `C001`) | `demo123` | Unit-level readiness analytics, heatmaps, cohort wellness metrics |
| **Welfare Officer** | `welfare@demo.com` (Code: `W001`) | `demo123` | Interventions, psychological support cases, peer check-in monitoring |
| **Personnel** | `p001@demo.com` (Code: `P001`) | `demo123` | Personal daily check-in, self-reflection, SOS support, wellness tips |

---

## ⚡ One-Click Quick Start Scripts

All one-click `.bat` runners are located in the project root directory:

### 1. Start Everything at Once
Double click **`start_all.bat`** in the project root.  
This launches:
1. Backend Server on `http://127.0.0.1:8000`
2. Web Dashboard on `http://localhost:5173`
3. Mobile Web App on `http://localhost:5174`

### 2. Start Individual Components
- **`start_backend.bat`** — Starts FastAPI server on port 8000 and establishes ADB port forwarding for USB debugging.
- **`start_web_dashboard.bat`** — Starts the React Web Dashboard on port 5173.
- **`start_mobile_web.bat`** — Starts the Personnel Mobile Web App on port 5174.
- **`start_live_backend.bat`** — Starts the FastAPI server and launches a public HTTPS Cloudflare Tunnel (`cloudflared.exe`) so external phones can connect over the internet.
- **`run_on_chrome.bat`** — Launches Flutter mobile app directly in Google Chrome with CanvasKit renderer.
- **`run_on_phone.bat`** — Runs Flutter app on connected Android phone via ADB.
- **`install_to_phone.bat`** — Installs `ManRakshak.apk` to connected Android device.
- **`build_apk.bat`** — Builds a release APK from Flutter source code.

---

## 🛠️ Manual Step-by-Step Execution Guide

### 1. Backend API Server (FastAPI)

```powershell
# Step 1: Navigate to backend directory
cd backend

# Step 2: Activate the Python Virtual Environment
# Windows PowerShell / CMD:
..\venv\Scripts\activate.bat
# or if local backend venv:
.\venv\Scripts\activate

# Step 3: (First time only) Install dependencies
pip install -r requirements.txt

# Step 4: Run database migrations / seed database
python scripts/seed.py

# Step 5: Start the Uvicorn ASGI Server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Server will be available at `http://127.0.0.1:8000` and Swagger UI at `http://127.0.0.1:8000/docs`.

---

### 2. Commander & Admin Web Dashboard (React)

```powershell
# Step 1: Navigate to web dashboard directory
cd web_dashboard

# Step 2: Install Node modules (if not already installed)
npm install

# Step 3: Start Vite development server
npm run dev
```
Dashboard opens at `http://localhost:5173`.

---

### 3. Personnel Mobile Web App (React PWA)

```powershell
# Step 1: Navigate to mobile web app directory
cd mobile_web_app

# Step 2: Install dependencies (if not already installed)
npm install

# Step 3: Start Vite development server on port 5174
npm run dev -- --port 5174
```
Access in browser or mobile emulator at `http://localhost:5174`.

---

### 4. Native Mobile App (Flutter / Android APK)

#### Option A: Run in Google Chrome
```powershell
cd mobile_app
flutter run -d chrome --web-renderer canvaskit
```

#### Option B: Run on Connected Physical Android Device (USB)
```powershell
# Step 1: Forward local backend port to mobile device
adb reverse tcp:8000 tcp:8000

# Step 2: Run Flutter application
cd mobile_app
flutter run -d <your-device-id>
```

#### Option C: Install Pre-built APK Directly
```powershell
adb install -r ManRakshak.apk
```

---

### 5. Docker Full-Stack Deployment

To run the entire ecosystem (Backend + PostgreSQL + Web Dashboard) in isolated containers:

```powershell
# Start all containers in background
docker compose up -d --build

# View container logs
docker compose logs -f

# Stop all containers
docker compose down
```

---

## 🔑 Environment Variables & API Keys Reference

### Backend `.env` Configuration (`backend/.env`)

```env
# ─── Database Configuration ────────────────────────────────────────────────
# SQLite for local development:
DATABASE_URL=sqlite:///./manrakshak.db
# PostgreSQL for production/Docker:
# DATABASE_URL=postgresql://postgres:password@localhost:5432/manrakshak

# ─── Security & Authentication ─────────────────────────────────────────────
JWT_SECRET=supersecretjwtkey_please_change_me_to_32_chars_random_string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

# ─── Cross-Origin Resource Sharing (CORS) ──────────────────────────────────
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,http://localhost:3000,http://127.0.0.1:5173,http://127.0.0.1:5174

# ─── Privacy & Anonymization Engine ────────────────────────────────────────
ANALYTICS_MIN_COHORT_SIZE=5
RATE_LIMIT_LOGIN=5

# ─── AI / LLM Gateway (OpenRouter) ─────────────────────────────────────────
AI_PROVIDER=openrouter
OPEN_ROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPEN_ROUTER_MODEL=qwen/qwen3.8-27b:free
OPEN_ROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_REQUEST_TIMEOUT_SECONDS=30.0
```

### Frontend `.env` Configuration (`web_dashboard/.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### OpenRouter AI LLM Key Setup

The platform includes an AI Gateway that generates psychological insights, morale assessments, and wellness summaries without leaking PII.

1. Register or log in at **[OpenRouter.ai](https://openrouter.ai/)**.
2. Go to **[Keys](https://openrouter.ai/keys)** and click **Create Key**.
3. Paste the key into `backend/.env` under `OPEN_ROUTER_API_KEY=sk-or-v1-...`.
4. The default model `qwen/qwen3.8-27b:free` or `meta-llama/llama-3.3-70b-instruct:free` is completely **free** with zero credit requirements.

---

## 📡 API Endpoints Reference (FastAPI v1)

Base URL: `http://localhost:8000/api/v1`

### 1. Authentication & Identity (`/auth`)
- `POST /api/v1/auth/login` — Login with email/user_code and password; returns JWT token + user role.
- `POST /api/v1/auth/refresh` — Refresh expired access token.
- `GET /api/v1/auth/me` — Retrieve current authenticated user profile and permissions.
- `POST /api/v1/auth/logout` — Invalidate current session.

### 2. Personnel Wellness Check-ins (`/wellness`)
- `POST /api/v1/wellness/checkin` — Submit daily wellness metrics (sleep hours, quality, mood, energy, stress, workload).
- `GET /api/v1/wellness/history` — Get personal check-in history.
- `GET /api/v1/wellness/trends` — 7-day and 30-day individual trend analytics.

### 3. Commander & Unit Analytics (`/analytics`)
- `GET /api/v1/analytics/readiness` — Aggregate unit readiness index (enforces k-anonymity cohort privacy).
- `GET /api/v1/analytics/heatmaps` — Stress, fatigue, and morale heatmaps across units.
- `GET /api/v1/analytics/trends` — Multi-week operational fatigue and burnout projections.

### 4. Interventions & Psychological Support (`/interventions` & `/support`)
- `GET /api/v1/interventions` — List proactive welfare interventions and recommendations.
- `POST /api/v1/interventions` — Trigger or schedule a welfare check / counseling session.
- `POST /api/v1/support/sos` — Anonymous emergency SOS trigger with priority dispatch.
- `GET /api/v1/support/resources` — Offline wellness drills, breathing exercises, and counseling contacts.

### 5. AI Copilot & Privacy Firewall (`/ai` & `/privacy`)
- `POST /api/v1/ai/insights` — Generate unit wellness summary using privacy-filtered LLM prompts.
- `POST /api/v1/ai/risk-assessment` — Evaluate collective fatigue risks and operational stress factors.
- `GET /api/v1/privacy/audit-log` — Cryptographic privacy audit logs demonstrating compliance with differential privacy rules.

### 6. Administration & User Management (`/admin` & `/personnel`)
- `GET /api/v1/admin/users` — List personnel under administrative scope.
- `POST /api/v1/admin/users` — Provision new user accounts and assign unit roles.
- `GET /api/v1/admin/units` — Manage battalions, companies, and platoons.
- `GET /api/v1/admin/system-health` — Real-time database, cache, and API gateway health metrics.

---

## 🗄️ Database Management & Seeding

### SQLite Database
- Database file: `backend/manrakshak.db`
- Inspectable using DB Browser for SQLite or VS Code SQLite Viewer extension.

### Re-seeding Data
To wipe and re-seed the database with 50 personnel profiles and 30 days of simulated operational data:
```powershell
cd backend
..\venv\Scripts\activate.bat
python scripts/seed.py
```

### Verifying All Core Workflows
Run the automated end-to-end workflow verification script:
```powershell
cd backend
..\venv\Scripts\activate.bat
python scripts/verify_v1_workflows.py
```

---

## 🧪 Automated Testing & Validation

The backend contains a test suite with 100+ tests covering authentication, RBAC, differential privacy, SQL injection resistance, and rate limiting.

Run the test suite:
```powershell
cd backend
..\venv\Scripts\activate.bat
pytest
```
*Current test suite status:* **106 Passed, 7 Skipped, 0 Failures (100% Pass Rate).**

---

## ❓ Troubleshooting & FAQs

### Q: How do I access the backend API from my physical mobile device?
1. **Via USB Cable:** Connect your Android phone with USB Debugging enabled, then run `adb reverse tcp:8000 tcp:8000`. The app will connect directly to `http://127.0.0.1:8000/api/v1`.
2. **Via Local Wi-Fi:** Ensure your computer and phone are on the same Wi-Fi network. Find your PC's IP using `ipconfig` (e.g., `192.168.1.50`), and configure the mobile app to connect to `http://192.168.1.50:8000/api/v1`.
3. **Via Public HTTPS Tunnel:** Run `start_live_backend.bat`. It will create a secure Cloudflare HTTPS URL that works anywhere over mobile data.

### Q: Port 8000 or 5173 is already in use
Run the following in PowerShell to terminate existing processes:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000
# Kill process by PID (e.g., PID 1234)
taskkill /F /PID 1234
```

### Q: Where are logs saved?
- Uvicorn logs are outputted directly to the console or background task logs.
- SQLite database logs and queries can be monitored in `backend/manrakshak.db`.

---

**© 2026 ManRakshak AI — Smart India Hackathon (SIH)**
