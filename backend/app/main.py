from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from contextlib import asynccontextmanager
import uvicorn

# from app.core.config import settings
# from app.api.routes import terminology, fhir, auth, mapping
# from app.db.database import engine, Base
# from app.services.background_tasks import start_background_tasks

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     Base.metadata.create_all(bind=engine)
#     await start_background_tasks()
#     yield
#     # Shutdown
#     pass

app = FastAPI(
    title="NAMASTE-ICD11 Integration API",
    description="FHIR R4-compliant terminology microservice for AYUSH healthcare systems",
    version="1.0.0",
    # lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# app.include_router(auth.router, prefix="/auth", tags=["authentication"])
# app.include_router(terminology.router, prefix="/terminology", tags=["terminology"])
# app.include_router(fhir.router, prefix="/fhir", tags=["fhir"])
# app.include_router(mapping.router, prefix="/mapping", tags=["mapping"])

@app.get("/")
async def root():
    return {"message": "NAMASTE-ICD11 Integration API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "namaste-icd11-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
