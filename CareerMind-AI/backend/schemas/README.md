# Data Schemas (`backend/schemas`)

## Overview
Defines Pydantic models for data validation, request parsing, and response serialization across API boundaries.

## Responsibilities
- **Request Models**: Input validation for file uploads, job description submissions, and interview answers.
- **Response Models**: Strict Data Transfer Objects (DTOs) preventing internal state leakage.
- **Engine Schemas**: Data contract interfaces passed between internal backend engines.
