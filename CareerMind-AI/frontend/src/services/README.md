# API Client Services (`frontend/src/services`)

## Overview
Axios/Fetch HTTP client instances, endpoint abstractions, and interceptor pipelines.

## Responsibilities
- Centralized Axios client with automatic Bearer token injection.
- Response interceptors for global error handling and automatic token renewal.
- Domain-specific service modules (`resumeService`, `matchService`, `interviewService`).
