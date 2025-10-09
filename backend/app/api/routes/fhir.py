from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import FHIRBundleRequest
from app.services.fhir_service import FHIRService
from app.services.mapping_service import MappingService
from app.core.security import get_current_user
from app.models.database import User, AuditLog
from datetime import datetime

router = APIRouter()

@router.post("/create-bundle")
async def create_fhir_bundle(
    request: FHIRBundleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create FHIR Bundle with dual coding support"""
    
    try:
        fhir_service = FHIRService()
        
        bundle = fhir_service.generate_bundle(
            diagnoses=request.diagnoses,
            patient_id=request.patient_id,
            encounter_id=request.encounter_id,
            practitioner_id=request.practitioner_id
        )
        
        # Create audit log
        audit = AuditLog(
            user_id=current_user.username,
            action="CREATE",
            resource_type="Bundle",
            resource_id=bundle["id"],
            metadata={"diagnoses_count": len(request.diagnoses)}
        )
        db.add(audit)
        db.commit()
        
        return bundle
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bundle creation failed: {str(e)}"
        )

@router.post("/concept-map")
async def create_concept_map(
    source_system: str,
    target_system: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate FHIR ConceptMap resource"""
    
    try:
        # Get mappings from database
        from app.models.database import ConceptMapping
        
        mappings = db.query(ConceptMapping).filter(
            ConceptMapping.source_system == source_system,
            ConceptMapping.target_system == target_system,
            ConceptMapping.is_validated == True
        ).all()
        
        if not mappings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No validated mappings found"
            )
        
        fhir_service = FHIRService()
        concept_map = fhir_service.generate_concept_map(
            source_system=source_system,
            target_system=target_system,
            mappings=[
                {
                    "source_code": m.source_code,
                    "target_code": m.target_code,
                    "equivalence": m.equivalence,
                    "confidence_score": m.confidence_score
                }
                for m in mappings
            ]
        )
        
        return concept_map
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ConceptMap creation failed: {str(e)}"
        )

@router.post("/validate-bundle")
async def validate_fhir_bundle(
    bundle: dict,
    current_user: User = Depends(get_current_user)
):
    """Validate FHIR Bundle structure (basic validation)"""
    
    try:
        # Basic validation checks
        if bundle.get("resourceType") != "Bundle":
            raise ValueError("Invalid resourceType, must be 'Bundle'")
        
        if not bundle.get("entry"):
            raise ValueError("Bundle must contain at least one entry")
        
        # Validate each entry has required fields
        for entry in bundle.get("entry", []):
            if not entry.get("resource"):
                raise ValueError("Entry must contain a resource")
            
            resource = entry["resource"]
            if not resource.get("resourceType"):
                raise ValueError("Resource must have resourceType")
        
        return {
            "valid": True,
            "message": "Bundle validation passed",
            "entries_count": len(bundle.get("entry", []))
        }
        
    except ValueError as e:
        return {
            "valid": False,
            "message": str(e)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )
