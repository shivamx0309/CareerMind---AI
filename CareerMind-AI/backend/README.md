# Backend Subsystem (FastAPI)

## Overview
The `backend` directory houses the core application logic, API routers, database configurations, and specialized AI/ML intelligence engines for CareerMind AI.

## Key Responsibilities
- High-performance asynchronous API endpoints powered by FastAPI and Uvicorn.
- Modular engine boundaries isolating resume parsing, NLP, traditional ML, deep learning, LLM orchestration, and RAG.
- Clean architectural layers: `api` -> `services` -> `engines` -> `database`.

## Module Directory Guide
- `api/`: Route declarations and API version controllers (`v1`).
- `core/`: Global settings, JWT security, custom middleware, and logging.
- `database/`: SQLAlchemy 2.0 async session factories, base models, and connection pools.
- `schemas/`: Pydantic V2 schemas for strict data validation and serialization.
- `services/`: Business orchestrators mediating between controllers and engines.
- `resume_engine/`: Document parsers (PDF, DOCX, OCR) and ATS structure scoring.
- `nlp_engine/`: Spacy / Transformers tokenizers and taxonomy-backed skill extraction.
- `ml_engine/`: Scikit-learn / LightGBM models for candidate rating and feature ranking.
- `dl_engine/`: PyTorch deep learning embeddings, bi-encoders, and cross-encoders.
- `llm_engine/`: Ollama local LLM drivers, prompt management, and cloud fallbacks.
- `rag_engine/`: Vector database indexing, hybrid retrieval, and knowledge ingestion.
- `matching_engine/`: Multi-dimensional candidate-job alignment and gap analysis.
- `interview_engine/`: AI mock interview question generator and adaptive rubric evaluation.
- `tests/`: Comprehensive unit, integration, and regression test suites.
