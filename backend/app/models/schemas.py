from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class CodeSystemType(str, Enum):
    """Supported code systems"""
    NAMASTE = "namaste"
    ICD11_TM2 = "icd11_tm2"
    ICD11_BIOMEDICINE = "icd11_biomedicine"

class AyushSystem(str, Enum):
    """Ayush system types"""
    AYURVEDA = "ayurveda"
    SIDDHA = "siddha"
    UNANI = "unani"

class EquivalenceType(str, Enum):
    """Mapping equivalence types"""
    EXACT = "exact"
    EQUIVALENT = "equivalent"
    WIDER = "wider"
    NARROWER = "narrower"
    INEXACT = "inexact"

# ===== Request/Response Models =====
class TerminologyCodeBase(BaseModel):
    """Base terminology code model"""
    code: str = Field(..., min_length=1, max_length=100)
    display: str = Field(..., min_length=1, max_length=500)
    system: CodeSystemType
    definition: Optional[str] = None
    ayush_system: Optional[AyushSystem] = None
    category: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None

class TerminologyCodeResponse(TerminologyCodeBase):
    """Terminology code response"""
    id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class SearchRequest(BaseModel):
    """Search terminology request"""
    query: str = Field(..., min_length=1, max_length=200)
    system: Optional[CodeSystemType] = None
    ayush_system: Optional[AyushSystem] = None
    limit: int = Field(default=10, ge=1, le=50)
    offset: int = Field(default=0, ge=0)

class SearchResponse(BaseModel):
    """Search results response"""
    results: List[TerminologyCodeResponse]
    total: int
    query: str
    system: Optional[CodeSystemType] = None

class TranslateRequest(BaseModel):
    """Code translation request"""
    code: str = Field(..., min_length=1)
    source_system: CodeSystemType
    target_system: CodeSystemType

class ConceptMappingResponse(BaseModel):
    """Concept mapping response"""
    source_code: str
    source_system: CodeSystemType
    target_code: str
    target_system: CodeSystemType
    equivalence: EquivalenceType
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    is_validated: bool = False
    
    class Config:
        from_attributes = True

class TranslateResponse(BaseModel):
    """Translation results"""
    source: TerminologyCodeResponse
    mappings: List[ConceptMappingResponse]
    total_mappings: int

class FHIRBundleRequest(BaseModel):
    """FHIR Bundle creation request"""
    patient_id: Optional[str] = None
    diagnoses: List[TerminologyCodeBase]
    encounter_id: Optional[str] = None
    practitioner_id: Optional[str] = None

# ===== Authentication Models =====
class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Token payload data"""
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(BaseModel):
    """User registration"""
    username: str = Field(..., min_length=3, max_length=100)
    email: str
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True