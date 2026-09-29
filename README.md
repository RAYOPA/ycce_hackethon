# 🛡️ ManRakshak AI — Police Wellness & Stress Management Platform

<div align="center">

![ManRakshak AI](https://img.shields.io/badge/ManRakshak-AI%20Powered-blue?style=for-the-badge&logo=shield)
![SIH 2024](https://img.shields.io/badge/SIH-2024%20Hackathon-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-green?style=for-the-badge&logo=fastapi)
![Flutter](https://img.shields.io/badge/Flutter-3.x-blue?style=for-the-badge&logo=flutter)
![React](https://img.shields.io/badge/React-19-cyan?style=for-the-badge&logo=react)
![XGBoost](https://img.shields.io/badge/XGBoost-AI-red?style=for-the-badge)

**An AI-driven platform to proactively monitor, predict, and manage the psychological wellness of police personnel.**

[📖 Documentation](#documentation) • [🚀 Quick Start](#quick-start) • [🏗️ Architecture](#architecture) • [📡 API Reference](#api-reference)

</div>

---

## 📋 Overview

ManRakshak AI is a comprehensive, full-stack organizational wellness platform purpose-built for law enforcement agencies. It uses **XGBoost-powered risk prediction** with **SHAP explainability**, real-time monitoring, intervention tracking, and a privacy-first multi-role access control system.

### 🎯 Key Features

| Feature | Description |
|---|---|
| 🤖 **AI Risk Engine** | XGBoost + SHAP for burnout & stress prediction with explainable factors |
| 📊 **Web Dashboard** | React 19 + TypeScript dashboard for commanders and welfare officers |
| 📱 **Mobile App** | Flutter app for personnel daily check-ins and support requests |
| 🌐 **Mobile Web** | Lightweight React PWA for browser-based mobile access |
| 🔐 **RBAC Auth** | JWT-based multi-role authentication (Personnel, Commander, Welfare Officer, Admin) |
| 🔒 **Privacy-First** | K-anonymity analytics, data minimization, audit trail |
| 🚨 **Interventions** | Automated alerts + manual intervention management |
| 💬 **AI Chat** | OpenRouter (Qwen LLM) powered wellness assistant |

---

## 🏗️ Project Structure

```
ManRakshak/
├── 📂 backend/              # FastAPI REST API server
│   ├── app/
│   │   ├── ai/              # AI Gateway (OpenRouter + ML inference)
│   │   ├── api/v1/          # REST route handlers
│   │   ├── core/            # Config, DB, security utilities
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── security/        # RBAC authorization policies
│   │   └── services/        # Business logic layer
│   ├── migrations/          # Alembic DB migrations
│   ├── tests/               # Pytest test suites
│   ├── Dockerfile
│   └── requirements.txt
│
├── 📂 web_dashboard/        # React 19 + TypeScript + TailwindCSS
│   ├── src/
│   │   ├── components/      # Reusable UI components
│   │   ├── features/        # Feature-based modules
│   │   ├── contexts/        # React context providers
│   │   └── layouts/         # Page layout templates
│   ├── Dockerfile
│   └── package.json
│
├── 📂 mobile_app/           # Flutter mobile app (Android/iOS)
│   ├── lib/                 # Dart source code
│   ├── assets/              # Images, fonts, icons
│   └── pubspec.yaml
│
├── 📂 mobile_web_app/       # React PWA (mobile browser)
│   ├── src/
│   └── package.json
│
├── 📂 ai_engine/            # Standalone ML training module
│   ├── model.py             # XGBoost + SHAP training pipeline
│   └── models/              # Trained model artifacts (.pkl)
│
├── 📂 data_generation/      # Synthetic data generation scripts
├── 📂 api/                  # Standalone API utilities
├── 📂 docs/                 # Additional documentation
│
├── 📄 docker-compose.yml    # Full stack Docker orchestration
├── 📄 COMMANDS.md           # All run commands reference
└── 📄 README.md             # This file
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Mayank-Kamdi/SIH_ManRakshak.git
cd SIH_ManRakshak

# Configure environment
cp backend/.env.example backend/.env
# Edit backend/.env with your secrets (see COMMANDS.md)

# Start all services
docker-compose up -d

# Access:
# Backend API:    http://localhost:8000
# Web Dashboard:  http://localhost:8080
# Mobile Web:     http://localhost:8081
# API Docs:       http://localhost:8000/api/v1/openapi.json
```

### Option 2: Manual Setup

See **[COMMANDS.md](./COMMANDS.md)** for step-by-step setup of each component.

---

## 📚 Documentation

| Document | Description |
|---|---|
| [COMMANDS.md](./COMMANDS.md) | All run commands, API keys, URL references |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | System architecture & component design |
| [docs/BACKEND.md](./docs/BACKEND.md) | Backend API server documentation |
| [docs/FRONTEND.md](./docs/FRONTEND.md) | Web dashboard & mobile app docs |
| [docs/AUTHENTICATION.md](./docs/AUTHENTICATION.md) | Auth system, JWT, RBAC |
| [docs/DATABASE.md](./docs/DATABASE.md) | Database schema & migrations |
| [docs/DOCKER.md](./docs/DOCKER.md) | Docker & deployment guide |
| [docs/AI_ENGINE.md](./docs/AI_ENGINE.md) | AI/ML system documentation |

---

## 👥 User Roles

| Role | Access | Platform |
|---|---|---|
| **Personnel** | Submit check-ins, view own data, request support | Mobile App / Mobile Web |
| **Commander** | View unit dashboard, anonymized stats | Web Dashboard |
| **Welfare Officer** | Full wellness data, interventions, reports | Web Dashboard |
| **Admin** | System administration, user management | Web Dashboard |

---

## 🧠 AI System

- **Model**: XGBoost Classifier (calibrated probability outputs)
- **Explainability**: SHAP TreeExplainer (top-3 risk factors per prediction)
- **LLM Chat**: OpenRouter → Qwen 3.8-27B (free tier)
- **Training Data**: Synthetic temporal welfare data (13 features)
- **Risk Factors**: Sleep deviation, mood trends, night duty frequency, workload, deployment duration

---

## 🔐 Security Features

- JWT access + refresh tokens
- bcrypt password hashing
- Rate limiting on auth endpoints (5 req/min)
- K-anonymity enforced on analytics (min cohort: 5)
- HTTPS security headers (HSTS, X-Frame-Options, nosniff)
- Audit logging for sensitive operations
- Organization-scoped resource access

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.11, FastAPI, SQLAlchemy 2.0, Alembic |
| **Database** | PostgreSQL 15 (production) / SQLite (dev) |
| **Auth** | JWT (python-jose), bcrypt (passlib) |
| **AI/ML** | XGBoost, SHAP, scikit-learn, pandas |
| **LLM** | OpenRouter API (Qwen 3.8-27B free) |
| **Web Frontend** | React 19, TypeScript, Vite, TailwindCSS, Recharts |
| **Mobile** | Flutter 3.x, Dart, fl_chart, flutter_secure_storage |
| **Mobile Web** | React, TypeScript, Vite, TailwindCSS |
| **Containerization** | Docker, Docker Compose |
| **Reverse Proxy** | Nginx (in Docker) |

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Mayank-Kamdi/SIH_ManRakshak/issues)
- **Hackathon Repo**: [RAYOPA/ycce_hackethon](https://github.com/RAYOPA/ycce_hackethon)
