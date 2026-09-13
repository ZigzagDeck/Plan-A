# Plan-A: Geospatial Landslide Risk & Early-Warning Platform

[![CI](https://github.com/ZigzagDeck/Plan-A/actions/workflows/ci.yml/badge.svg)](https://github.com/ZigzagDeck/Plan-A/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.5%2B-F7931E.svg)](https://scikit-learn.org/)
[![PostGIS](https://img.shields.io/badge/PostGIS-16--3.4-336791.svg)](https://postgis.net/)

**Plan-A** is an operational geospatial landslide risk estimation and early-warning decision-support platform designed for disaster management authorities, emergency responders, and watershed monitoring teams.

The platform integrates a checksum-verified **8-variable Random Forest ML inference engine** trained on the Geological Survey of India (GSI) North-Eastern Region (NER) dataset, a **FastAPI backend** with PostGIS spatial indexing, an automated **alert lifecycle & notification engine**, and a modern **Streamlit GIS Dashboard**.

---

## 🏛️ Repository Architecture

```text
Plan-A/
├── backend/            FastAPI application, domain services, database models, and API tests
│   ├── app/
│   │   ├── api/        REST routers (/predict, /alerts, /simulation, /exposure, /notifications)
│   │   ├── core/       Pydantic settings and risk threshold configuration
│   │   ├── db/         SQLAlchemy async session, transaction manager, and seed utilities
│   │   ├── models/     PostGIS spatial entities (RiskCell, RiskSnapshot, Asset, Alert)
│   │   ├── model_artifacts/  Production Random Forest joblib bundle & model manifest
│   │   ├── realtime/   WebSocket alert broadcast hub (ws://.../ws/alerts)
│   │   ├── scheduler/  APScheduler runtime for background sensor observation ingestion
│   │   └── services/   Domain engines (ArtifactModelGateway, AlertService, ExposureService)
│   ├── migrations/     Alembic PostGIS database migrations
│   └── tests/          Unit and integration test suites
├── frontend/           Streamlit GIS & Early-Warning Dashboard
│   ├── components/     Reusable UI modules (GIS Folium map, Plotly charts, API client, custom styles)
│   ├── dashboard.py    Interactive 5-module dashboard application
│   └── requirements.txt  Frontend Python dependencies
├── ml/                 Reproducible Random Forest ML training pipeline
│   ├── artifacts/      Model bundle and manifest mirrors
│   ├── plan_a_ml/      Feature engineering, spatial group holdout, and pipeline validation
│   └── train.py        Training entrypoint CLI
├── scripts/            Automated end-to-end verification tools
│   └── verify_e2e.py   End-to-end ML, API, alert engine, and UI verification script
├── data/               Dataset contracts and local storage guidance
├── docs/               System architecture, model contracts, and design decisions
└── infra/              Docker Compose deployment manifests
```

---

## 🚀 Quickstart Guide

### 1. Environment Setup

Clone the repository and create a Python virtual environment:

```bash
git clone https://github.com/ZigzagDeck/Plan-A.git
cd Plan-A

python -m venv .venv

# On Windows (PowerShell):
.venv\Scripts\activate

# On Linux / macOS:
source .venv/bin/activate
```

Install backend and frontend dependencies:

```bash
python -m pip install -e './backend[test]'
python -m pip install -r frontend/requirements.txt
```

---

### 2. Launch the Streamlit GIS Dashboard

Run the interactive dashboard directly:

```bash
streamlit run frontend/dashboard.py --server.port 8501
```

Open your browser at **[http://localhost:8501](http://localhost:8501)**.

#### 🌟 Key Dashboard Features:
1. **🌍 Geospatial Early-Warning Center**: Interactive Folium GIS map showing North-Eastern Region (NER) terrain polygons, 2,000m hazard buffer rings, and nearby critical infrastructure (schools, hospitals, highways, power substations, bridges).
2. **⚡ ML Real-Time Prediction Studio**: Live inference interface against the real Random Forest model with sliders for all 8 parameters, preset scenarios (Dry Season, Monsoon Surge, Cloudburst), Plotly speedometer gauge dials, and transparent model driver tags.
3. **🌧️ Monsoon Rainfall Simulator & Ops**: Surge multiplier sandbox (0.5x to 5.0x baseline rainfall), dynamic response curves, and telemetry sensor ingestion queue (`POST /api/v1/rainfall/observations`).
4. **🚨 Alert Lifecycle & Dispatch Hub**: Live alert feed with operator audit buttons (`Acknowledge`, `Verify`, `Resolve`) and FCM mobile push notification subscription simulator.
5. **📊 Model Manifest & ML Analytics**: Inspection of the manifest metadata, SHA-256 verification, Random Forest hyperparameters, feature importance weights, and spatial group holdout split statistics.

---

### 3. Run the FastAPI Backend

To start the REST API server:

```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```

- **Health Probe**: <http://127.0.0.1:8000/health>
- **Readiness Probe**: <http://127.0.0.1:8000/health/ready>
- **Swagger Documentation**: <http://127.0.0.1:8000/docs>
- **WebSocket Alert Stream**: `ws://127.0.0.1:8000/ws/alerts`

---

### 4. Run with Docker Compose (PostGIS Included)

Launch the complete stack (FastAPI backend + PostGIS PostgreSQL 16):

```bash
cp .env.example .env
docker compose up --build
```

- Backend API: `http://localhost:8000`
- PostgreSQL / PostGIS: `localhost:5432`

Seed initial North-Eastern Region (NER) sample risk cells and exposure assets:

```bash
python backend/app/db/seed.py
```

---

## 🔬 Machine Learning Pipeline

Plan-A runs a production **RandomForestClassifier** trained on geospatial slope-failure records across Arunachal Pradesh and Northeast India.

### 8-Variable Feature Pipeline
| Feature | Type | Description | Manifest Weight |
|---|---|---|---|
| `Elevation_m` | Topographic | Elevation above sea level in meters | **23.8%** |
| `Slope_deg` | Topographic | Terrain incline in degrees (0° - 90°) | **17.4%** |
| `Soil_Sand_pct` | Geotechnical | Sand grain fraction percentage | **16.4%** |
| `Soil_Clay_pct` | Geotechnical | Clay soil fraction percentage | **13.1%** |
| `Rainfall_mm` | Hydrological | 24-hour cumulative precipitation | **10.9%** |
| `Rainfall_7day_antecedent_mm` | Hydrological | 7-day cumulative antecedent rainfall | **10.0%** |
| `Rainfall_Event_ERA5_mm` | Reanalysis | ERA5 reanalysis event precipitation | **6.0%** |
| `Aspect_deg` | Topographic | Slope azimuth orientation (0° - 359°) | **2.5%** |

### Validation & Provenance
- **Artifact**: `backend/app/model_artifacts/landslide_model.joblib`
- **Manifest**: `backend/app/model_artifacts/model_manifest.json` (SHA-256 verified on startup)
- **Validation Strategy**: **Spatial Group Holdout** across 0.25° grid cells (zero spatial group leakage between training and test sets)
- **Metrics**: **ROC-AUC: 0.7769**, **PR-AUC: 0.6229**, Accuracy: 68.9%
- **Transparent Driver Explanations**: Rule-based percentile drivers (`High rainfall`, `Steep slope`, `High clay soil content`, `High elevation terrain`) returned alongside the probability score.

---

## 🚨 Early-Warning & Alert Engine

1. **Risk Threshold Classification**:
   - `LOW`: Score < 0.40
   - `MEDIUM`: 0.40 ≤ Score < 0.65
   - `HIGH`: 0.65 ≤ Score < 0.80 *(Triggers operational alert)*
   - `CRITICAL`: Score ≥ 0.80 *(Triggers emergency evacuation alert)*
2. **Alert State Machine**:
   ```text
   [Trigger: HIGH/CRITICAL] ──> ACTIVE ──> ACKNOWLEDGED ──> VERIFIED ──> RESOLVED
                                  │
                                  └──> [Surge in Risk] ──> ESCALATED
   ```
3. **Multi-Channel Dispatch**:
   - **WebSocket Stream**: Emits `alert.event` messages to connected command center dashboards (`ws://.../ws/alerts`).
   - **Push Notifications**: Firebase Cloud Messaging (FCM) integration with bounded exponential retry for field teams.

---

## 🧪 Quality Checks & Testing

The repository enforces strict continuous integration standards:

```bash
# Backend linting and formatting
ruff check backend
ruff format --check backend

# Backend unit test suite (62 tests)
pytest backend/tests -m "not integration"

# ML pipeline test suite (3 tests)
pytest ml/tests

# End-to-end integration and verification script
python scripts/verify_e2e.py
```

### GitHub Actions CI Workflow
Every pull request is automatically tested across 4 parallel jobs:
- **ML quality**: Validates model training scripts, data hygiene, and scenario checks.
- **Backend quality**: Ruff static analysis and unit tests.
- **PostGIS migrations**: Executes database migrations and integration test suite against live PostGIS container.
- **Backend container**: Validates production Docker container build.

---

## 📄 License & Provenance

Plan-A is an open-source geospatial early-warning prototype. Geological hazard assessment requires localized geotechnical field validation.
