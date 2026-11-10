import os
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import engine, Base, SessionLocal
import app.models # Ensure all SQLAlchemy models are registered
from app.services.seed_service import seed_database

# Routers
from app.api.brands_router import router as brands_router
from app.api.submissions_router import router as submissions_router
from app.api.review_router import router as review_router
from app.api.analytics_router import router as analytics_router
from app.api.settings_router import router as settings_router
from app.api.chat_router import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("LIFESPAN: Starting table creation...", flush=True)
    Base.metadata.create_all(bind=engine)
    print("LIFESPAN: Tables created. Seeding database...", flush=True)
    db = SessionLocal()
    try:
        seed_database(db)
        print("LIFESPAN: Database seeded successfully.", flush=True)
    finally:
        db.close()
    print("LIFESPAN: Yielding control to app...", flush=True)
    yield
    print("LIFESPAN: App shutting down...", flush=True)

app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Intelligent Brand Governance & Content Compliance Platform",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for seamless local dev & preview
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file serving for uploads (images, PDFs)
if settings.upload_dir.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.upload_dir)), name="uploads")

# Include Routers
app.include_router(brands_router)
app.include_router(submissions_router)
app.include_router(review_router)
app.include_router(analytics_router)
app.include_router(settings_router)
app.include_router(chat_router)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.version,
        "engine": "GEMINI_HYBRID" if settings.gemini_api_key else "DETERMINISTIC_RULES"
    }

# Production SPA static files mounting
frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    def serve_frontend_spa(full_path: str):
        target = frontend_dist / full_path
        if target.exists() and target.is_file():
            return FileResponse(target)
        return FileResponse(frontend_dist / "index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
