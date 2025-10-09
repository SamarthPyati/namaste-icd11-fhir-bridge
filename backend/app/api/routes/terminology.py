from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import (
    SearchRequest, SearchResponse, 
    TerminologyCodeResponse, CodeSystemType
)
from app.services.namaste_service import NamasteService
from app.services.icd11_service import ICD11Service
from app.core.security import get_current_user
from app.models.database import User
import tempfile
import os

router = APIRouter()

@router.post("/upload-namaste-csv")
async def upload_namaste_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload and process NAMASTE CSV file (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can upload data"
        )
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        service = NamasteService()
        result = await service.process_csv(tmp_file_path)
        return result
    finally:
        os.unlink(tmp_file_path)

@router.get("/sync-icd11")
async def sync_icd11(current_user: User = Depends(get_current_user)):
    """Synchronize with WHO ICD-11 API (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can sync data"
        )
    
    try:
        service = ICD11Service()
        result = await service.fetch_tm2_codes()
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync ICD-11 codes: {str(e)}"
        )

@router.post("/search", response_model=SearchResponse)
async def search_terminology(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Search terminology codes across systems"""
    
    try:
        results = []
        
        if request.system == CodeSystemType.NAMASTE or request.system is None:
            namaste_service = NamasteService()
            namaste_results = await namaste_service.search_codes(
                query=request.query,
                ayush_system=request.ayush_system.value if request.ayush_system else None,
                limit=request.limit,
                offset=request.offset
            )
            results.extend(namaste_results)
        
        if request.system == CodeSystemType.ICD11_TM2 or request.system is None:
            icd11_service = ICD11Service()
            icd11_results = await icd11_service.search_codes(
                query=request.query,
                limit=request.limit,
                offset=request.offset
            )
            results.extend(icd11_results)
        
        # Limit results
        results = results[:request.limit]
        
        return SearchResponse(
            results=[TerminologyCodeResponse(**r) for r in results],
            total=len(results),
            query=request.query,
            system=request.system
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/code/{system}/{code}", response_model=TerminologyCodeResponse)
async def get_code_details(
    system: CodeSystemType,
    code: str,
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific code"""
    
    try:
        if system == CodeSystemType.NAMASTE:
            service = NamasteService()
            result = await service.get_code_by_id(code)
        elif system == CodeSystemType.ICD11_TM2:
            service = ICD11Service()
            result = await service.search_codes(query=code, limit=1)
            result = result[0] if result else None
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid system"
            )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Code {code} not found in system {system}"
            )
        
        return TerminologyCodeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/codesystem/{system}")
async def get_fhir_codesystem(
    system: CodeSystemType,
    current_user: User = Depends(get_current_user)
):
    """Get FHIR CodeSystem resource"""
    
    try:
        if system == CodeSystemType.NAMASTE:
            service = NamasteService()
            return service.generate_fhir_codesystem()
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"CodeSystem generation not implemented for {system}"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
