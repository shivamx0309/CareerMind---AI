# Database Subsystem (`backend/database`)

## Overview
Manages relational data persistence, asynchronous SQLAlchemy sessions, entity-relationship models, and database migration routines.

## Responsibilities
- **Asynchronous ORM**: SQLAlchemy 2.0 async engine with PostgreSQL (`asyncpg`).
- **Model Declarations**: Declarative entity models located under `database/models/` (Users, Resumes, JobDescriptions, MatchResults, Interviews).
- **Session Management**: Scoped session lifecycle management and FastAPI dependency injection (`get_db`).
