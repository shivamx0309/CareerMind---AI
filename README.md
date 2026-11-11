# CareerMind AI 🚀
### Intelligent Career Intelligence, Resume Analytics & Interview Platform

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com/)
[![React 19](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev/)
[![Vite 8](https://img.shields.io/badge/Vite-8-646CFF.svg)](https://vitejs.dev/)
[![Tailwind CSS v4](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com/)
[![Alembic](https://img.shields.io/badge/Alembic-1.13+-red.svg)](https://alembic.sqlalchemy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📌 Overview

**CareerMind AI** is an AI-powered Career Intelligence and Job Readiness platform designed to bridge the gap between candidates' current qualifications and target industry roles. The platform features evidence-based resume extraction, multi-dimensional job description alignment, deterministic skill gap analysis, personalized weekly learning curriculums, and an AI mock interview simulator.

All five core functional capabilities are fully implemented, verified with comprehensive automated test suites (267 backend unit tests, 100% pass rate), and prepared for persistent production deployment.

---

## 🏛️ Deployment Architecture

CareerMind AI is configured for production deployment using decoupled modern hosting:

```text
┌─────────────────────────────────────────────────────────────┐
│                    Vercel Frontend (SPA)                    │
│   • React 19 + Vite 8 + Tailwind CSS v4                     │
│   • Dynamic API client: VITE_API_BASE_URL                   │
│   • vercel.json SPA wildcard rewrite to index.html          │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS / JSON REST
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Render Web Service (Backend)                │
│   • Python FastAPI + Uvicorn ASGI Application               │
│   • CORS Middleware configured for Vercel origin            │
│   • Non-blocking Health check endpoints (/ & /health)       │
└──────────────────────────────┬──────────────────────────────┘
                               │ Mounts /var/data
                               ▼
┌─────────────────────────────────────────────────────────────┐
│            Render Persistent Disk (/var/data, 1GB)          │
│   • Production SQLite Database: /var/data/careermind.db     │
│   • Persistent PDF Uploads:     /var/data/uploads/          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🌟 Five Implemented Capabilities

1. **Resume Intelligence**:
   - Automated parsing of PDF resumes using PyMuPDF and deterministic NLP extraction.
   - Extracts structured candidate profiles: contact details, education, technical skill taxonomies across 10 categories, work experience, projects, and certifications.
   - Secure server-side PDF storage with path-traversal guards and default resume management.

2. **Job Description Matching**:
   - Automated requirement parsing from raw job descriptions.
   - Weighted multi-dimensional scoring evaluating technical skills (mandatory vs. preferred), experience tenure, and education credentials.
   - Clear, explainable match breakdown with prioritized improvement recommendations.

3. **Skill Gap Analysis**:
   - Compares candidate resume profiles against curated industry role benchmarks (e.g. Software Development Engineer, Backend Developer, Data Scientist, ML Engineer).
   - Categorizes skills into exact matches, semantically related competencies, and missing requirements with deterministic readiness scoring.

4. **Personalized Learning Roadmap**:
   - Converts assessed skill gaps into structured, multi-week learning curriculums based on weekly time availability (5h, 10h, 15h, 20h/week).
   - Module-by-module milestones with progress tracking, estimated completion timelines, and filtered view states.

5. **AI Mock Interview Simulator**:
   - Interactive practice interviews across Technical, Behavioral (STAR rubric), Project-Based, and Mixed question types.
   - Role-specific questions tailored to candidate-identified skill gaps without exposing answers in question views.
   - Real-time response evaluation grading concept coverage, relevance, structure, and completeness.

---

## ⚙️ Environment Variables

### Backend Configuration (Render Web Service)

| Variable | Required | Description | Example / Recommended Value |
| :--- | :---: | :--- | :--- |
| `DATABASE_URL` | Yes (Prod) | Path to SQLite database file. Automatically creates directory. | `sqlite:////var/data/careermind.db` |
| `CAREERMIND_UPLOAD_DIR` | Yes (Prod) | Physical path for persistent PDF storage. | `/var/data/uploads` |
| `FRONTEND_ORIGINS` | Yes (Prod) | Comma-separated list of allowed frontend origins for CORS. | `http://localhost:5173,https://YOUR-FRONTEND.vercel.app` |
| `PYTHON_VERSION` | Optional | Specifies Python runtime on Render. | `3.11.9` |

> **Note for Local Development**: If `DATABASE_URL` and `CAREERMIND_UPLOAD_DIR` are unset, the backend automatically defaults to local files (`CareerMind-AI/backend/careermind.db` and `CareerMind-AI/data/uploads`).

### Frontend Configuration (Vercel)

| Variable | Required | Description | Example / Recommended Value |
| :--- | :---: | :--- | :--- |
| `VITE_API_BASE_URL` | Yes (Prod) | Base URL pointing to the deployed Render backend API. | `https://YOUR-BACKEND.onrender.com/api/v1` |

> **Note for Local Development**: If `VITE_API_BASE_URL` is unset, Vite development server uses the built-in proxy in `vite.config.js` (`/api/v1` -> `http://127.0.0.1:8000`).

---

## 🚀 Deployment Guide

### Part 1: Render Backend Deployment

1. **Create Web Service**:
   - Log into [Render Dashboard](https://dashboard.render.com/) and click **New +** -> **Web Service**.
   - Connect your GitHub repository (`CareerMind---AI`).
2. **Configure Service Settings**:
   - **Name**: `careermind-ai-backend`
   - **Region**: Choose closest to your target audience (e.g., Oregon or Frankfurt).
   - **Branch**: `shivam` (or `main`)
   - **Root Directory**: `CareerMind-AI/backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. **Attach Persistent Disk**:
   - Under **Disks**, click **Add Disk**.
   - **Name**: `careermind-data`
   - **Mount Path**: `/var/data`
   - **Size**: `1 GB` (sufficient for SQLite database and thousands of PDF resumes).
4. **Set Environment Variables**:
   - `DATABASE_URL` = `sqlite:////var/data/careermind.db`
   - `CAREERMIND_UPLOAD_DIR` = `/var/data/uploads`
   - `FRONTEND_ORIGINS` = `http://localhost:5173,https://YOUR-FRONTEND.vercel.app`
   - `PYTHON_VERSION` = `3.11.9`
5. **Health Check Path**:
   - Set **Health Check Path** to `/health`.
6. Click **Create Web Service**.

---

### Part 2: Vercel Frontend Deployment

1. **Import Project**:
   - Log into [Vercel Dashboard](https://vercel.com/) and click **Add New...** -> **Project**.
   - Select your GitHub repository.
2. **Configure Project Settings**:
   - **Root Directory**: Click Edit and select `CareerMind-AI/frontend`.
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
3. **Set Environment Variables**:
   - Add `VITE_API_BASE_URL`:
     ```text
     https://<YOUR-RENDER-SERVICE-NAME>.onrender.com/api/v1
     ```
4. **Deploy**:
   - Click **Deploy**.
   - Copy the deployed Vercel URL (e.g. `https://careermind-ai.vercel.app`) and update the `FRONTEND_ORIGINS` variable in your Render dashboard.

---

## 💾 Initial Data & PDF Migration (Preserving Local Data)

The local repository contains existing user data:
- Database: `CareerMind-AI/backend/careermind.db`
- Resumes: `CareerMind-AI/data/uploads/*.pdf`

When deploying to Render with a brand-new persistent disk at `/var/data`, you have two options:

### Option A: Fresh Database with Migrations (Recommended for Clean Launch)
If you wish to start with a fresh production database schema:
1. In the Render Shell tab of your service, run:
   ```bash
   alembic upgrade head
   ```
2. The schema will be created with all tables up to the latest revision (`ee34607e5025`).

### Option B: Migrating Existing Local SQLite & Uploads to Render Persistent Disk
To carry over your existing candidate profile, default resume, and history:
1. Enable **SSH** in your Render service settings.
2. Transfer your local `careermind.db` to the persistent disk using SCP:
   ```bash
   scp -P <RENDER_SSH_PORT> CareerMind-AI/backend/careermind.db <RENDER_SSH_USER>@<RENDER_SSH_HOST>:/var/data/careermind.db
   ```
3. Transfer uploaded PDF resumes to `/var/data/uploads/`:
   ```bash
   scp -P <RENDER_SSH_PORT> -r CareerMind-AI/data/uploads/* <RENDER_SSH_USER>@<RENDER_SSH_HOST>:/var/data/uploads/
   ```
4. Verify file permissions inside the Render Shell:
   ```bash
   ls -la /var/data/
   ls -la /var/data/uploads/
   ```
   All database records referencing `file_id` will immediately find their corresponding PDF files at `/var/data/uploads/{file_id}.pdf`.

---

## 🛠️ Local Development

### 1. Backend Setup
```bash
cd CareerMind-AI/backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations (if starting clean)
alembic upgrade head

# Launch development server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
Backend runs on `http://127.0.0.1:8000`. Swagger documentation available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup
```bash
cd CareerMind-AI/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```
Frontend runs on `http://localhost:5173`. Requests to `/api` are automatically proxied to `http://127.0.0.1:8000`.

---

## 🩺 Production Health Checks

Test the live status of the deployment without hitting the database:

- **Root Ping**:
  ```bash
  curl -i https://YOUR-BACKEND.onrender.com/
  # Expected: HTTP 200 {"message": "Welcome to CareerMind AI", "status": "running"}
  ```

- **Health Check**:
  ```bash
  curl -i https://YOUR-BACKEND.onrender.com/health
  # Expected: HTTP 200 {"status": "healthy", "application": "CareerMind AI"}
  ```

---

## ⚠️ Known Hosting Limitations

1. **Render Free/Hobby Tier Cold Starts**:
   - Render Web Services on the free plan spin down after 15 minutes of inactivity. The first incoming request may experience a 30–50 second delay while the container starts up.
   - For a production portfolio demo, consider keeping the service warm or upgrading to an Starter instance.
2. **SQLite Single-Writer Concurrency**:
   - SQLite with WAL mode and `PRAGMA foreign_keys=ON` is exceptionally fast and reliable for single-instance web services (like Render Web Service with a single replica).
   - It is not suited for multi-container horizontal autoscaling. For multi-replica horizontal scale, migrate to Managed PostgreSQL.

---

## 📜 License
MIT License. All rights reserved.
