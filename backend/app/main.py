from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

import uvicorn

app = FastAPI(
    title=settings.app_name,
    description="FHIR-Compliant Terminology Bridge for India's EMRs",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AYUR-SANKET API",
        "version": settings.app_version,
        "description": "FHIR-Compliant Terminology Bridge for India's EMRs",
        "docs": "/docs"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "ayur-sanket-api",
        "version": settings.app_version
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )