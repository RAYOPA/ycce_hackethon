# ManRakshak Backend V1

FastAPI, PostgreSQL, SQLAlchemy backend for the ManRakshak organizational wellness platform.

## 1. Project Overview
This backend provides secure APIs, role-based access control, and data persistence for both the Flutter Personnel Mobile App and the React Organization Web Dashboard.

## 2. Requirements
- Python 3.12+
- PostgreSQL 15+ (Local or Docker)

## 3. PostgreSQL Setup
If you have Docker installed, you can start the database using:
```bash
docker-compose up -d
```
Otherwise, ensure PostgreSQL is running locally on port 5432 with the credentials specified in the `.env` file.

## 4. Environment Setup
Copy the environment example:
```bash
cp .env.example .env
```

## 5. Install Dependencies
```bash
python -m venv venv
# On Windows
.\venv\Scripts\Activate.ps1
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

## 6. Run Migrations
Generate the initial database schema using Alembic:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 7. Seed Database
Generate mock personnel, units, check-ins, and demo accounts:
```bash
python scripts/seed.py
```

## 8. Start FastAPI
```bash
uvicorn app.main:app --reload
```
The server will start at `http://localhost:8000`.

## 9. API Documentation
FastAPI automatically generates documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 10. Demo Credentials
All demo accounts use the password: `demo123`

- Personnel: `p001@demo.com`
- Welfare Officer: `welfare@demo.com`
- Commander: `commander@demo.com`
- Administrator: `admin@demo.com`

## 11. Security Notes
- Passwords are hashed using bcrypt.
- JWT tokens are issued with a 24-hour expiration.
- All endpoints are protected by Role-Based Access Control (RBAC).
- Commander roles are strictly prohibited from viewing individual wellness records.
- Audit logs track access events without storing sensitive PHI data.
