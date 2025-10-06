from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

app = FastAPI(
    title="NAMASTE-ICD11 Integration API",
    description="FHIR R4-compliant terminology microservice for AYUSH healthcare systems",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Svelte dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NAMASTE-ICD11 Integration API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "namaste-icd11-api"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
