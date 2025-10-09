from typing import List, Dict, Any
from datetime import datetime
from app.models.schemas import TerminologyCodeBase
import uuid
import logging

logger = logging.getLogger(__name__)

class FHIRService:
    """Service for FHIR R4 resource generation"""
    
    def generate_bundle(
        self,
        diagnoses: List[TerminologyCodeBase],
        patient_id: str = None,
        encounter_id: str = None,
        practitioner_id: str = None
    ) -> Dict[str, Any]:
        """Generate FHIR R4 Bundle with dual coding"""
        
        bundle_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        # Create bundle entries
        entries = []
        
        # Add Patient resource (if ID provided)
        if patient_id:
            entries.append(self._create_patient_entry(patient_id))
        
        # Add Practitioner resource (if ID provided)
        if practitioner_id:
            entries.append(self._create_practitioner_entry(practitioner_id))
        
        # Add Encounter resource
        encounter_resource = self._create_encounter(encounter_id, patient_id, practitioner_id)
        entries.append(encounter_resource)
        
        # Add Condition resources for each diagnosis
        for diagnosis in diagnoses:
            condition = self._create_condition(
                diagnosis,
                patient_id,
                encounter_resource["resource"]["id"]
            )
            entries.append(condition)
        
        # Create complete bundle
        bundle = {
            "resourceType": "Bundle",
            "id": bundle_id,
            "type": "transaction",
            "timestamp": timestamp,
            "entry": entries
        }
        
        logger.info(f"Generated FHIR Bundle with {len(entries)} entries")
        return bundle
    
    def _create_patient_entry(self, patient_id: str) -> Dict[str, Any]:
        """Create Patient resource entry"""
        return {
            "fullUrl": f"urn:uuid:{patient_id}",
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "identifier": [
                    {
                        "system": "https://healthid.ndhm.gov.in",
                        "value": patient_id
                    }
                ]
            },
            "request": {
                "method": "POST",
                "url": "Patient"
            }
        }
    
    def _create_practitioner_entry(self, practitioner_id: str) -> Dict[str, Any]:
        """Create Practitioner resource entry"""
        return {
            "fullUrl": f"urn:uuid:{practitioner_id}",
            "resource": {
                "resourceType": "Practitioner",
                "id": practitioner_id,
                "identifier": [
                    {
                        "system": "https://hpr.abdm.gov.in",
                        "value": practitioner_id
                    }
                ]
            },
            "request": {
                "method": "POST",
                "url": "Practitioner"
            }
        }
    
    def _create_encounter(
        self,
        encounter_id: str,
        patient_id: str,
        practitioner_id: str
    ) -> Dict[str, Any]:
        """Create Encounter resource"""
        encounter_id = encounter_id or str(uuid.uuid4())
        
        return {
            "fullUrl": f"urn:uuid:{encounter_id}",
            "resource": {
                "resourceType": "Encounter",
                "id": encounter_id,
                "status": "finished",
                "class": {
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                    "code": "AMB",
                    "display": "ambulatory"
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                } if patient_id else None,
                "participant": [
                    {
                        "individual": {
                            "reference": f"Practitioner/{practitioner_id}"
                        }
                    }
                ] if practitioner_id else [],
                "period": {
                    "start": datetime.utcnow().isoformat()
                }
            },
            "request": {
                "method": "POST",
                "url": "Encounter"
            }
        }
    
    def _create_condition(
        self,
        diagnosis: TerminologyCodeBase,
        patient_id: str,
        encounter_id: str
    ) -> Dict[str, Any]:
        """Create Condition resource with dual coding"""
        condition_id = str(uuid.uuid4())
        
        # Build coding array (supports dual coding)
        coding = [
            {
                "system": self._get_system_url(diagnosis.system),
                "code": diagnosis.code,
                "display": diagnosis.display
            }
        ]
        
        return {
            "fullUrl": f"urn:uuid:{condition_id}",
            "resource": {
                "resourceType": "Condition",
                "id": condition_id,
                "clinicalStatus": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "active"
                        }
                    ]
                },
                "category": [
                    {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                                "code": "encounter-diagnosis",
                                "display": "Encounter Diagnosis"
                            }
                        ]
                    }
                ],
                "code": {
                    "coding": coding,
                    "text": diagnosis.display
                },
                "subject": {
                    "reference": f"Patient/{patient_id}"
                } if patient_id else None,
                "encounter": {
                    "reference": f"Encounter/{encounter_id}"
                },
                "recordedDate": datetime.utcnow().isoformat()
            },
            "request": {
                "method": "POST",
                "url": "Condition"
            }
        }
    
    def _get_system_url(self, system: str) -> str:
        """Get FHIR system URL for code system"""
        system_urls = {
            "namaste": "https://namaste.ayush.gov.in/CodeSystem/disorders",
            "icd11_tm2": "http://id.who.int/icd/release/11/mms/26",
            "icd11_biomedicine": "http://id.who.int/icd/release/11/mms"
        }
        return system_urls.get(system, system)
    
    def generate_concept_map(
        self,
        source_system: str,
        target_system: str,
        mappings: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate FHIR R4 ConceptMap resource"""
        
        return {
            "resourceType": "ConceptMap",
            "id": f"{source_system}-to-{target_system}",
            "url": f"https://ayur-sanket.gov.in/ConceptMap/{source_system}-to-{target_system}",
            "version": "1.0.0",
            "name": f"{source_system.upper()}To{target_system.upper()}",
            "title": f"Mapping from {source_system.upper()} to {target_system.upper()}",
            "status": "active",
            "experimental": False,
            "date": datetime.utcnow().isoformat(),
            "publisher": "AYUR-SANKET Team",
            "sourceUri": self._get_system_url(source_system),
            "targetUri": self._get_system_url(target_system),
            "group": [
                {
                    "source": self._get_system_url(source_system),
                    "target": self._get_system_url(target_system),
                    "element": [
                        {
                            "code": mapping["source_code"],
                            "target": [
                                {
                                    "code": mapping["target_code"],
                                    "equivalence": mapping["equivalence"],
                                    "comment": f"Confidence: {mapping['confidence_score']:.2f}"
                                }
                            ]
                        }
                        for mapping in mappings
                    ]
                }
            ]
        }
