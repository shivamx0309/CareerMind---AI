
from fastapi import FastAPI

from api.v1.endpoints.resume import router as resume_router
from api.v1.endpoints.jobs import router as jobs_router
from api.v1.endpoints.onboarding import router as onboarding_router
from api.v1.endpoints.skills import router as skills_router
from api.v1.endpoints.learning import router as learning_router
from api.v1.endpoints.interviews import router as interviews_router


app = FastAPI(
    title="CareerMind AI",
    description=(
        "AI-powered Career Intelligence "
        "and Resume Assessment Platform"
    ),
    version="0.1.0",
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
