# 🐳 ManRakshak AI — Docker & Deployment Guide

## Overview

ManRakshak uses **Docker Compose** to orchestrate all services. The stack consists of 4 containers:
1. `db` — PostgreSQL 15 database
2. `backend` — FastAPI Python server
3. `web_dashboard` — React admin dashboard (served by Nginx)
4. `mobile_web_app` — React mobile PWA (served by Nginx)

---

## 📋 Prerequisites

```bash
# Check Docker is installed
docker --version      # Docker 20.10+
docker compose version  # Compose v2.x

# Check Docker is running
docker info
```

---

## ⚙️ Configuration Before First Launch

### 1. Create Backend `.env`

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
# REQUIRED — choose one:
DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak  # Docker
# DATABASE_URL=sqlite:///./manrakshak.db  # Local dev only

JWT_SECRET=your_min_32_char_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=http://localhost:5173,http://localhost:8080,http://localhost:8081

AI_PROVIDER=openrouter
OPEN_ROUTER_API_KEY=sk-or-v1-your-key-here
OPEN_ROUTER_MODEL=qwen/qwen3.8-27b:free
OPEN_ROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_REQUEST_TIMEOUT_SECONDS=30.0

ANALYTICS_MIN_COHORT_SIZE=5
RATE_LIMIT_LOGIN=5
```

### 2. Create Frontend `.env` Files

```bash
# Web Dashboard
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > web_dashboard/.env.local

# Mobile Web App
echo "VITE_API_BASE_URL=http://localhost:8000/api/v1" > mobile_web_app/.env.local
```

---

## 🚀 Starting the Full Stack

```bash
# Start all services (background)
docker-compose up -d

# Start all services (foreground — see all logs)
docker-compose up

# Start with force rebuild
docker-compose up -d --build
```

### Expected Output

```
[+] Running 4/4
 ✔ Container manrakshak-db-1              Started
 ✔ Container manrakshak-backend-1         Started
 ✔ Container manrakshak-web_dashboard-1   Started
 ✔ Container manrakshak-mobile_web_app-1  Started
```

### Service URLs After Startup

| Service | URL | Description |
|---|---|---|
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Web Dashboard** | http://localhost:8080 | Admin web interface |
| **Mobile Web** | http://localhost:8081 | Personnel mobile interface |
| **PostgreSQL** | localhost:5433 | Database (port 5433 to avoid conflict with local PG) |

---

## 📋 Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: manrakshak
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./models:/app/models  # Mount trained ML models

  web_dashboard:
    build:
      context: ./web_dashboard
    ports:
      - "8080:80"
    depends_on:
      - backend

  mobile_web_app:
    build:
      context: ./mobile_web_app
    ports:
      - "8081:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 🔧 Docker Management Commands

### Service Lifecycle

```bash
# View running containers
docker-compose ps

# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop, remove containers AND volumes (⚠️ DELETES DATABASE DATA)
docker-compose down -v

# Restart a specific service
docker-compose restart backend

# Scale backend (multiple instances)
docker-compose up -d --scale backend=2
```

### Viewing Logs

```bash
# Follow all service logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f backend
docker-compose logs -f db
docker-compose logs -f web_dashboard

# Show last 100 lines
docker-compose logs --tail=100 backend
```

### Rebuilding After Code Changes

```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

---

## 🗃️ Database Operations in Docker

### Run Migrations

```bash
# Apply all pending migrations
docker-compose exec backend alembic upgrade head

# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history
```

### Access PostgreSQL Shell

```bash
# Connect to the database
docker-compose exec db psql -U postgres -d manrakshak

# Useful commands inside psql:
\dt                    # List tables
\d users               # Describe users table
SELECT count(*) FROM wellness_checkins;
\q                     # Quit
```

### Database Backup & Restore

```bash
# Backup database
docker-compose exec db pg_dump -U postgres manrakshak > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U postgres manrakshak < backup_20240115.sql
```

---

## 🏗️ Individual Dockerfiles

### Backend Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for psycopg2 and XGBoost
RUN apt-get update && apt-get install -y \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir shap xgboost pandas joblib scikit-learn

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Web Dashboard / Mobile Web Dockerfile

```dockerfile
# web_dashboard/Dockerfile (same pattern for mobile_web_app)
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Nginx Config (for React SPAs)

```nginx
# nginx.conf
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # React SPA routing — serve index.html for all routes
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## 🌐 Production Deployment

### Environment Considerations

For production deployment, update these settings:

1. **Change database password** — never use `password` in production
2. **Set strong JWT_SECRET** — minimum 32 random characters
3. **Restrict CORS_ORIGINS** — only your actual domain(s)
4. **Enable HTTPS** — use Nginx with SSL termination or a load balancer
5. **Set persistent volume** — ensure `postgres_data` volume is on persistent storage

### Production `docker-compose.prod.yml`

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: manrakshak
    volumes:
      - /data/postgres:/var/lib/postgresql/data  # Absolute path
    restart: always

  backend:
    image: manrakshak-backend:latest
    env_file: ./backend/.env
    environment:
      - DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/manrakshak
    depends_on:
      - db
    restart: always

  web_dashboard:
    image: manrakshak-dashboard:latest
    restart: always

  mobile_web_app:
    image: manrakshak-mobile-web:latest
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-prod.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt  # SSL certs
    depends_on:
      - backend
      - web_dashboard
      - mobile_web_app
    restart: always
```

### Deploy to Production

```bash
# Build and push images
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml push

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Run migrations on first deploy
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 🔍 Health Checks

```bash
# Backend health
curl http://localhost:8000/health
# Expected: {"status": "ok", "message": "ManRakshak Server is operational"}

# Backend root
curl http://localhost:8000/
# Expected: {"message": "Welcome to ManRakshak API"}

# PostgreSQL health (via Docker)
docker-compose exec db pg_isready -U postgres
# Expected: /var/run/postgresql:5432 - accepting connections
```

---

## 🛠️ Cloudflare Tunnel (Quick Public Access)

For demos or mobile device testing without a domain:

```powershell
# Start backend first
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Start tunnel (generates a public HTTPS URL)
cloudflared.exe tunnel --url http://localhost:8000
# Output: https://xxxx-xxxx.trycloudflare.com

# OR use the provided script
start_live_backend.bat
```

Update `OPEN_ROUTER_API_KEY` and `CORS_ORIGINS` to include the tunnel URL.

---

## 🐛 Docker Troubleshooting

### Container won't start

```bash
# Check container logs for errors
docker-compose logs backend

# Check if port is already in use
netstat -ano | findstr :8000
netstat -ano | findstr :8080
```

### Database connection refused

```bash
# Verify db container is healthy
docker-compose ps
# db column should show "healthy"

# Verify DATABASE_URL uses 'db' as host (not localhost)
# DATABASE_URL=postgresql://postgres:password@db:5432/manrakshak
#                                              ^^-- container service name
```

### Frontend shows blank page

```bash
# Check Nginx logs
docker-compose logs web_dashboard

# Verify build succeeded
docker-compose exec web_dashboard ls /usr/share/nginx/html
# Should list: index.html, assets/, etc.
```

### Out of disk space

```bash
# Clean unused Docker resources
docker system prune -f

# Clean including unused volumes (⚠️ careful)
docker system prune --volumes -f

# Check disk usage
docker system df
```
