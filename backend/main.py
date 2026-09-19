import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings
from backend.database.database import init_db

# Create FastAPI app
app = FastAPI(
    title="Deadline Guardian API",
    description="Real-Time Intelligent Deadline Management & Recommendation System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Deadline Guardian API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import routers
from backend.api.auth import router as auth_router
from backend.api.tasks import router as tasks_router
from backend.api.dashboard import router as dashboard_router
from backend.api.notifications import router as notifications_router
from backend.api.guardian import router as guardian_router

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(tasks_router, prefix="/tasks", tags=["Tasks"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(guardian_router, prefix="/guardian", tags=["Guardian"])
