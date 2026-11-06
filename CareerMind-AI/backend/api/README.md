# API Routing Layer (`backend/api`)

## Overview
The API layer defines RESTful endpoints, request routing, dependency injection, and versioning protocols.

## Responsibilities
- **API Versioning**: Standardized `/api/v1` namespace with route segmentation in `v1/endpoints/`.
- **Controller Endpoints**: Resume upload/parse, JD analysis, matching, interview sessions, user auth.
- **Error Handling**: Global exception capture and standard JSON response formatting.
