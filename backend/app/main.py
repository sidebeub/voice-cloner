from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .core import settings
from .api import voices

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Voice cloning application API"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "samples"), exist_ok=True)
os.makedirs(os.path.join(settings.UPLOAD_DIR, "generated"), exist_ok=True)

# Mount static files for serving audio
app.mount("/audio", StaticFiles(directory=settings.UPLOAD_DIR), name="audio")

# Include routers
app.include_router(voices.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Voice Cloner API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
