# CareerMind AI 🚀
### Next-Generation AI Career Intelligence & Talent Acquisition Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 18+](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Executive Overview
**CareerMind AI** is an enterprise-grade career intelligence and talent matching ecosystem engineered to revolutionize technical recruitment, candidate skill evaluation, and career progression. Combining deep learning, local and cloud-based Large Language Models (LLMs), semantic vector retrieval (RAG), and deterministic NLP pipelines, CareerMind AI automates end-to-end resume intelligence, candidate-job alignment, and adaptive mock interviews.

---

## 🏛️ Core Architectural Pillars

| Pillar | Subsystem | Core Technologies |
| :--- | :--- | :--- |
| **Resume Intelligence** | `backend/resume_engine` | PyMuPDF, pdfplumber, python-docx, OCR (Tesseract) |
| **NLP & Skill Extraction** | `backend/nlp_engine` | spaCy, HuggingFace NER, ESCO/O*NET Skill Taxonomy |
| **Machine Learning** | `backend/ml_engine` | Scikit-learn, LightGBM, XGBoost, Ranking Algorithms |
| **Deep Learning** | `backend/dl_engine` | PyTorch, SentenceTransformers, Bi/Cross-Encoders |
| **Generative AI & Local LLMs** | `backend/llm_engine` | Ollama (Llama 3 / Mistral), LangChain, vLLM, OpenAI / Gemini |
| **RAG Knowledge Engine** | `backend/rag_engine` | ChromaDB, Qdrant, BM25 Hybrid Retrieval, LangChain |
| **Job-Candidate Matching** | `backend/matching_engine` | Cosine Distance, Weighted Skill Graphs, Semantic Match |
| **AI Interview Simulator** | `backend/interview_engine` | Dynamic Prompting, Speech-to-Text, Real-time Rubrics |
| **API & Core Infrastructure** | `backend/api`, `backend/core` | FastAPI, Pydantic v2, SQLAlchemy 2.0 (Async), PostgreSQL, Redis |
| **Frontend Experience** | `frontend/` | React 18, Vite, Tailwind CSS, Lucide Icons, Chart.js |

---

## 📂 Project Directory Structure

```text
CareerMind-AI/
├── backend/                  # FastAPI high-performance backend application
│   ├── api/                  # REST API routes and versioning (/api/v1)
│   ├── core/                 # Global configuration, logging, and security
│   ├── database/             # SQLAlchemy async models, connections, and migrations
│   ├── dl_engine/            # Deep learning models, embeddings, and transformers
│   ├── interview_engine/     # Dynamic AI interview simulator and rubrics
│   ├── llm_engine/           # Local and cloud LLM orchestrators and prompts
│   ├── matching_engine/      # Resume-to-Job matching and gap analysis
│   ├── ml_engine/            # Traditional ML algorithms, scoring, and classification
│   ├── nlp_engine/           # NLP pipeline, tokenization, and skill extraction
│   ├── rag_engine/           # Retrieval-Augmented Generation & vector stores
│   ├── resume_engine/        # Document parsing, section segmentation, and ATS scoring
│   ├── schemas/              # Pydantic validation models (DTOs)
│   ├── services/             # Business logic orchestration layer
│   └── tests/                # Unit, integration, and performance test suites
├── data/                     # Raw, processed, and temporary upload storage
├── docs/                     # Architectural specs, API documentation, and ADRs
├── frontend/                 # Modern React dashboard and client UI
│   ├── public/               # Public web assets and favicon
│   └── src/                  # Application source code (components, pages, hooks, etc.)
├── knowledge_base/           # RAG reference documents, taxonomies, and vector indexes
├── ml_models/                # Checkpoints, fine-tuned weights, and pre-trained models
├── notebooks/                # Jupyter research and exploratory data analysis notebooks
├── sample_data/              # Anonymized sample resumes and job descriptions
├── scripts/                  # Automation, data ingestion, and migration scripts
├── .env.example              # Centralized environment variable template
├── .gitignore                # Comprehensive Git exclusion rules
├── docker-compose.yml        # Multi-container orchestration (Backend, Frontend, DB, Redis, Chroma)
└── README.md                 # Project master documentation
```

---

## 🗺️ 16-Phase Progressive Roadmap

1. **Phase 1: Project Scaffolding & Architecture Foundation** *(Current)*
2. **Phase 2: Database Modeling & Migration Infrastructure**
3. **Phase 3: Core Security, Authentication & Configuration**
4. **Phase 4: Resume Parsing Engine (PDF/DOCX/OCR)**
5. **Phase 5: NLP Pipeline & Skill Extraction Engine**
6. **Phase 6: Traditional Machine Learning Scoring & Classification**
7. **Phase 7: Deep Learning Embeddings & Semantic Representations**
8. **Phase 8: Job Description Intelligence & Matching Engine**
9. **Phase 9: Local LLM Orchestration & Fallback Engine**
10. **Phase 10: RAG Knowledge Engine & Vector Store Integration**
11. **Phase 11: Dynamic AI Interview Simulator**
12. **Phase 12: Business Logic Services & Unified API Layer**
13. **Phase 13: Frontend Architecture & Design System Setup**
14. **Phase 14: Interactive Frontend Feature Implementation**
15. **Phase 15: End-to-End Testing, Benchmarking & Optimization**
16. **Phase 16: Containerization, CI/CD & Production Deployment**

---

## 🚀 Getting Started (Initialization)
This project is currently in **Phase 1 (Scaffolding)**. Application dependencies and source code will be progressively developed in subsequent phases.

```bash
# Clone the repository
git clone https://github.com/your-username/CareerMind-AI.git
cd CareerMind-AI

# Duplicate environment template
cp .env.example .env
```

---

## 📜 License & Compliance
This project is licensed under the MIT License. All sample datasets adhere to privacy and GDPR anonymization standards.
