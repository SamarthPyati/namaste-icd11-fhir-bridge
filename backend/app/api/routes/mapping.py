from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import (
    TranslateRequest, TranslateResponse,
    TerminologyCodeResponse, ConceptMappingResponse
)
from app.services.mapping_service import MappingService
from app.services.namaste_service import NamasteService
from app.core.security import get_current_user
from app.models.database import User

router = APIRouter()

@router.post("/translate", response_model=TranslateResponse)
async def translate_code(
    request: TranslateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Translate code from source to target system"""
    
    try:
        # Get source code details
        if request.source_system == "namaste":
            service = NamasteService()
            source_code = await service.get_code_by_id(request.code)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Source system {request.source_system} not supported"
            )
        
        if not source_code:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Source code {request.code} not found"
            )
        
        # Get mappings
        mapping_service = MappingService()
        mappings = await mapping_service.translate_code(
            code=request.code,
            source_system=request.source_system.value,
            target_system=request.target_system.value,
            db=db
        )
        
        return TranslateResponse(
            source=TerminologyCodeResponse(**source_code),
            mappings=[ConceptMappingResponse.from_orm(m) for m in mappings],
            total_mappings=len(mappings)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )

@router.post("/generate-mappings")
async def generate_mappings(
    source_system: str,
    target_system: str,
    threshold: float = 0.3,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate intelligent mappings between systems (Admin only)"""
    
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can generate mappings"
        )
    
    try:
        service = MappingService()
        
        # Run in background if background_tasks provided
        if background_tasks:
            background_tasks.add_task(
                service.generate_mappings,
                source_system=source_system,
                target_system=target_system,
                threshold=threshold,
                db=db
            )
            return {
                "message": "Mapping generation started in background",
                "source_system": source_system,
                "target_system": target_system
            }
        else:
            mappings = await service.generate_mappings(
                source_system=source_system,
                target_system=target_system,
                threshold=threshold,
                db=db
            )
            return {
                "message": "Mappings generated successfully",
                "mappings_count": len(mappings),
                "source_system": source_system,
                "target_system": target_system
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Mapping generation failed: {str(e)}"
        )

@router.get("/validate-mapping/{mapping_id}")
async def validate_mapping(
    mapping_id: int,
    is_valid: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate a concept mapping (Expert/Admin only)"""
    
    if current_user.role not in ["admin", "expert"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only experts can validate mappings"
        )
    
    from app.models.database import ConceptMapping
    from datetime import datetime
    
    mapping = db.query(ConceptMapping).filter(ConceptMapping.id == mapping_id).first()
    
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found"
        )
    
    mapping.is_validated = is_valid
    mapping.validated_by = current_user.username
    mapping.validation_date = datetime.utcnow()
    
    db.commit()
    db.refresh(mapping)
    
    return {
        "message": "Mapping validation updated",
        "mapping_id": mapping_id,
        "is_validated": is_valid,
        "validated_by": current_user.username
    }