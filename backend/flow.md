# Backend Execution Flow

This document outlines the standard request lifecycle and execution flow of the ManRakshak backend.

## 1. Application Startup
- The FastAPI application (`app.main.app`) initializes.
- Environment variables are loaded securely via `app.core.config.Settings`.
- Database engine and connection pools are established via `app.core.database`.
- CORS middleware is configured based on `CORS_ORIGINS`.

## 2. Request Handling
- A client (Flutter App or React Web Dashboard) sends an HTTP request to an endpoint (e.g., `/api/v1/users`).
- FastAPI routes the request to the appropriate router registered in the main application (e.g., `app.api.v1`).

## 3. Dependency Injection (Database & Security)
- The endpoint requires a database session, injected via `Depends(get_db)`.
- `get_db` yields a `SessionLocal` instance for the lifetime of the request and safely closes it afterward in a `finally` block.
- For protected routes, `Depends(get_current_user)` checks the JWT token to ensure the user is authenticated and authorized via RBAC.

## 4. Business Logic & Services
- The route handler delegates complex logic to service layers if applicable (e.g., creating a new wellness check-in, assigning an intervention).
- ORM queries are executed using SQLAlchemy 2.0 models (`app.models`).

## 5. Database Interaction
- SQLAlchemy translates python ORM commands into optimized PostgreSQL queries.
- Operations are committed using `db.commit()` or rolled back on exceptions to maintain atomicity.
- Enums, Unique Constraints, and Check Constraints ensure data integrity directly at the PostgreSQL level.

## 6. Response
- The database result is returned as Pydantic schemas (from `app.schemas`), which serialize the SQLAlchemy models into JSON format.
- FastAPI automatically validates the response against the Pydantic schema before sending the HTTP response back to the client.
