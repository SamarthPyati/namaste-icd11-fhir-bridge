from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

import logging

from app.core.config import settings
from app.db.database import engine, Base
from app.db.mongodb import connect_mongodb, close_mongodb
from app.api.routes import auth, terminology, mapping, fhir

# TODO: Add logging_config.py in app/core/config
# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting AYUR-SANKET API...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    logger.info("✅ PostgreSQL tables created")
    
    # Connect to MongoDB
    connect_mongodb()
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AYUR-SANKET API...")
    close_mongodb()

app = FastAPI(
    title=settings.app_name,
    description="FHIR-Compliant Terminology Bridge for India's EMRs",
    version=settings.app_version,
    lifespan=lifespan, 
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

# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error occurred"}
    )

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(terminology.router, prefix="/terminology", tags=["Terminology"])
app.include_router(mapping.router, prefix="/mapping", tags=["Code Mapping"])
app.include_router(fhir.router, prefix="/fhir", tags=["FHIR Resources"])

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