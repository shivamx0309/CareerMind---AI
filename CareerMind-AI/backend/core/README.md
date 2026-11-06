# Core Subsystem (`backend/core`)

## Overview
The Core subsystem provides foundational application utilities, environment configuration, security primitives, and telemetry.

## Responsibilities
- **Pydantic Settings**: Centralized environment variable loading and validation (`config.py`).
- **Security & Cryptography**: Password hashing (bcrypt/argon2), JWT token issuance, and validation (`security.py`).
- **Logging & Observability**: Structured JSON logging, request tracing, and execution timing.
