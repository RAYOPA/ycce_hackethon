# Architectural & Implementation Decisions

This document logs the considerations and reasons behind significant architectural and code changes in the ManRakshak backend. It should be updated whenever new major architectural decisions are made.

## 1. Database Layer (SQLAlchemy 2.0)
**Date:** 2026-08-31

**Consideration:** Use SQLAlchemy 2.0 style syntax (`Mapped`, `mapped_column`) instead of SQLAlchemy 1.x style (`Column`, `String`).
* **Reason:** SQLAlchemy 2.0 provides better type hinting, stricter type checking with tools like mypy, and represents the modern, future-proof standard for Python ORMs.

**Consideration:** Extracted all Enums into a separate `enums.py` file.
* **Reason:** Centralizing enums (`UserRole`, `UserStatus`, `SupportRequestType`, etc.) prevents circular imports between models and provides a single source of truth for allowed database values.

**Consideration:** Used `uuid.uuid4()` for all primary keys instead of auto-incrementing integers.
* **Reason:** UUIDs provide better security (preventing ID enumeration attacks), make database merging easier in the future, and are universally unique across distributed systems.

**Consideration:** Implemented explicit `CheckConstraint` on wellness scores (e.g., `sleep_hours >= 0 AND sleep_hours <= 24`).
* **Reason:** Ensures critical data integrity at the PostgreSQL database level rather than exclusively relying on FastAPI application-level validations.

**Consideration:** Removed `cascade="all, delete-orphan"` from the `Organization` to `Unit` and `User` relationships.
* **Reason:** Prevents accidental deletion of an organization from silently cascading and permanently deleting all historical personnel data, support requests, and interventions. Soft deletes/status fields will be used instead.
