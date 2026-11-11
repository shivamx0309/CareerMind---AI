
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.v1.endpoints.resume import router as resume_router
from api.v1.endpoints.jobs import router as jobs_router
from api.v1.endpoints.onboarding import router as onboarding_router
from api.v1.endpoints.skills import router as skills_router
from api.v1.endpoints.learning import router as learning_router
from api.v1.endpoints.interviews import router as interviews_router
from api.v1.endpoints.dashboard import router as dashboard_router


app = FastAPI(
    title="CareerMind AI",
    description=(
        "AI-powered Career Intelligence "
        "and Resume Assessment Platform"
    ),
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# CORS Configuration: Support dynamic Vercel origin with localhost fallbacks
# ---------------------------------------------------------------------------
DEFAULT_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

frontend_origins_env = os.getenv("FRONTEND_ORIGINS")
if frontend_origins_env:
    extra_origins = [
        origin.strip()
        for origin in frontend_origins_env.split(",")
        if origin.strip()
    ]
    # Deduplicate while preserving order
    allowed_origins = list(dict.fromkeys(DEFAULT_ALLOWED_ORIGINS + extra_origins))
else:
    allowed_origins = DEFAULT_ALLOWED_ORIGINS

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)


# Register Career Profile Onboarding API
app.include_router(
    onboarding_router,
    prefix="/api/v1",
    tags=["Onboarding & Career Profile"],
)

# Register Resume Intelligence API
app.include_router(
    resume_router,
    prefix="/api/v1",
    tags=["Resume Intelligence"],
)

# Register Job Description Matching API
app.include_router(
    jobs_router,
    prefix="/api/v1",
    tags=["Job Matching"],
)

# Register Standalone Skill Gap Analysis API
app.include_router(
    skills_router,
    prefix="/api/v1",
    tags=["Skill Gap Analysis"],
)

# Register Personalized Learning Roadmap API
app.include_router(
    learning_router,
    prefix="/api/v1",
    tags=["Learning Roadmap"],
)

# Register AI Mock Interview Simulator API
app.include_router(
    interviews_router,
    prefix="/api/v1",
    tags=["Mock Interview Simulator"],
)

# Register Dashboard Career Insights API
app.include_router(
    dashboard_router,
    prefix="/api/v1",
    tags=["Dashboard Insights"],
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to CareerMind AI",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "application": "CareerMind AI",
    }
