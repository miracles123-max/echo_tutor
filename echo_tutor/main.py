from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from echo_tutor.api.routes import router
from echo_tutor.config import get_settings
import uvicorn

settings = get_settings()

app = FastAPI(
    title="Multi-Agent Learning System API",
    description="API for document/image reading with pronunciation and tutoring",
    version="1.0.0"
)

# CORS middleware for Vue.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
import os

# Include routers
app.include_router(router, prefix="/api/v1", tags=["learning"])

# Mount static files for audio
audio_dir = settings.upload_dir
os.makedirs(audio_dir, exist_ok=True)
app.mount("/audio", StaticFiles(directory=audio_dir), name="audio")

@app.get("/")
async def root():
    return {
        "message": "Multi-Agent Learning System API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "echo_tutor.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
