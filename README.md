# AYUR-SANKET

> **A FHIR-Compliant Terminology Bridge for India's EMRs**

[![Smart India Hackathon 2025](https://img.shields.io/badge/SIH-2025-orange.svg)](https://sih.gov.in/)
[![FHIR R4](https://img.shields.io/badge/FHIR-R4-blue.svg)](http://hl7.org/fhir/R4/)
[![Python](https://img.shields.io/badge/Python-3.9+-green.svg)](https://python.org/)
[![Svelte](https://img.shields.io/badge/Svelte-4.0+-red.svg)](https://svelte.dev/)

## What is AYUR-SANKET?

AYUR-SANKET is a lightweight, plug-and-play microservice that bridges traditional Indian medicine (NAMASTE codes) with global healthcare standards (ICD-11 TM2). It enables existing EMR systems to support Ayurveda, Siddha, and Unani treatments with full insurance eligibility and research compliance.

**Not a new EMR system** → **An intelligent add-on plugin for ANY existing EMR**

## Key Features

- **Plug-and-Play**: Works with any EMR system without modifications
- **Intelligent Mapping**: ML-powered translation between NAMASTE ↔ ICD-11 codes
- **Lightning Fast**: Sub-200ms API responses with Redis caching
- **FHIR Compliant**: Full FHIR R4 compatibility for global interoperability
- **ABHA Integration**: Seamless authentication with India's health account system
- **Real-time Sync**: Automated updates from WHO ICD-11 API

## Problem Solved

| **Before AYUR-SANKET** | **After AYUR-SANKET** |
|-------------------------|------------------------|
| ❌ Ayurveda treatments not eligible for insurance | ✅ Full insurance coverage with ICD-11 codes |
| ❌ Traditional medicine data trapped in silos | ✅ Standardized research data for policy decisions |
| ❌ EMRs can't handle traditional medicine codes | ✅ Any EMR supports NAMASTE + ICD-11 dual coding |
| ❌ Manual code lookup and translation | ✅ Intelligent auto-suggestions and validation |

## Tech Stack

### Backend
- **FastAPI** - High-performance async Python framework
- **PostgreSQL** - Structured data (mappings, audit logs)
- **MongoDB** - Flexible terminology storage
- **Redis** - High-speed caching
- **Celery** - Background task processing

### Frontend
- **Svelte/SvelteKit** - Modern, fast web framework
- **Tailwind CSS** - Responsive design system

### Standards & Compliance
- **FHIR R4** - Healthcare interoperability standard
- **ABHA OAuth 2.0** - National health authentication
- **SNOMED CT/LOINC** - Clinical terminology standards

## Build Application

### Step 1 - Set up the virtual environment 
```
python -m venv .venv                (Win)
.\venv\Scripts\activate
```
```
python3 -m venv .venv               (Mac/Linux)
source .venv/bin/activate
```

### Step 2 - Create a .env folder and add all the environment varibles there
```
mkdir .env
```

## Backend

### API
API endpoints

### DB
Creates and connect to the instance of the Database (engine)

### Models
Database schema required to store the data

### Services
Middleware services

<!-- 
## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose

### Installation

```bash
# Clone the repository
git clone https://github.com/team-sprint-schmeide/ayur-sanket.git
cd ayur-sanket

# Start services with Docker
docker-compose up -d

# Install backend dependencies
cd backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Start development servers
npm run dev          # Frontend (http://localhost:5173)
cd ../backend
uvicorn main:app --reload  # Backend (http://localhost:8000)
```

### Environment Setup

```bash
# Create .env file
DATABASE_URL=postgresql://user:password@localhost/namaste_db
MONGODB_URL=mongodb://localhost:27017/
ICD11_CLIENT_ID=your_icd11_client_id
ICD11_CLIENT_SECRET=your_icd11_client_secret
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
```

## API Usage

### Search Terminology
```bash
curl -X POST "http://localhost:8000/terminology/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "diabetes", "limit": 5}'
```

### Translate Codes
```bash
curl -X POST "http://localhost:8000/mapping/translate" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "NAMASTE001", 
    "source_system": "namaste",
    "target_system": "icd11_tm2"
  }'
```

### Generate FHIR Bundle
```bash
curl -X POST "http://localhost:8000/fhir/create-bundle" \
  -H "Content-Type: application/json" \
  -d '{
    "diagnoses": [
      {"code": "NAMASTE001", "system": "namaste", "display": "Vata Imbalance"}
    ]
  }'
```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Existing EMR  │───▶│  AYUR-SANKET    │───▶│  Insurance &    │
│     System      │    │     Plugin      │    │   Analytics     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  WHO ICD-11 API │
                    │  NAMASTE Portal │
                    │  ABHA System    │
                    └─────────────────┘
```

## Impact Metrics

- **Target**: 1000+ EMR integrations across India
- **Performance**: <200ms response time, 99.9% uptime
- **Accuracy**: 95%+ mapping confidence with ML validation
- **Coverage**: 4,500+ NAMASTE codes ↔ 529 ICD-11 TM2 categories
- **Market Impact**: Unlock ₹500+ crore Ayush insurance market

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## Testing

```bash
# Backend tests
cd backend
pytest tests/ --cov=app

# Frontend tests
cd frontend
npm test
```

## Deployment

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes deployment
kubectl apply -f k8s/
```

## Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **FHIR Implementation Guide**: `/docs/fhir-guide.md`
- **Integration Manual**: `/docs/emr-integration.md`
- **Deployment Guide**: `/docs/deployment.md`
-->
## Team Sprint Schmeide

**Smart India Hackathon 2025 - Problem Statement #26, SIH25026**

<!-- - **Backend Developers**: Vinay
- **Frontend Developer**: [Your Name]
- **FHIR Specialist**: [Your Name]
- **ML Engineer**: [Your Name]
- **Project Manager**: [Your Name] -->


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<!-- 
## 🙏 Acknowledgments

- Ministry of AYUSH for NAMASTE terminology standards
- World Health Organization for ICD-11 TM2 specifications
- National Health Authority for ABHA integration guidelines
- All India Institute of Ayurveda (AIIA) for domain expertise

---

** Making traditional medicine globally accessible, one API call at a time.**

For questions or support, reach out to: [your-email@domain.com]

 -->