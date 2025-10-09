from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Boolean, Index
from sqlalchemy.sql import func
from app.db.database import Base

class TerminologyEntry(Base):
    """Terminology codes storage"""
    __tablename__ = "terminology_entries"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, index=True, nullable=False)
    display = Column(String(500), nullable=False)
    system = Column(String(50), index=True, nullable=False)  # namaste, icd11_tm2, icd11_bio
    definition = Column(Text)
    ayush_system = Column(String(50))  # ayurveda, siddha, unani
    category = Column(String(200))
    properties = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_system_code', 'system', 'code'),
        Index('idx_display_search', 'display'),
    )

class ConceptMapping(Base):
    """Code mappings between systems"""
    __tablename__ = "concept_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    source_code = Column(String(100), index=True, nullable=False)
    source_system = Column(String(50), nullable=False)
    target_code = Column(String(100), index=True, nullable=False)
    target_system = Column(String(50), nullable=False)
    equivalence = Column(String(20))  # exact, equivalent, wider, narrower, inexact
    confidence_score = Column(Float)
    is_validated = Column(Boolean, default=False)
    validated_by = Column(String(100))
    validation_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index('idx_source_mapping', 'source_code', 'source_system'),
        Index('idx_target_mapping', 'target_code', 'target_system'),
    )

class AuditLog(Base):
    """Audit trail for compliance"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    action = Column(String(50))  # CREATE, READ, UPDATE, DELETE, SEARCH, TRANSLATE
    resource_type = Column(String(50))  # CodeSystem, ConceptMap, etc.
    resource_id = Column(String(100))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    _metadata = Column(JSON) # _metadata as metadata is a reserved column name in sqlalchemy
        
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_action_timestamp', 'action', 'timestamp'),
    )

class User(Base):
    """User management"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="user")  # admin, user, expert
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))