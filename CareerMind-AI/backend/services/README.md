# Services Business Logic Layer (`backend/services`)

## Overview
The Services layer acts as the business logic orchestrator, decoupling API controllers from domain-specific AI/ML engines and database access.

## Responsibilities
- **Workflow Orchestration**: Coordinate multi-engine operations (e.g., parse resume -> extract skills -> compute embeddings -> store to DB).
- **Transaction Boundaries**: Manage transactional integrity across multiple database operations.
- **External Integration**: Handle asynchronous background workers and caching.
