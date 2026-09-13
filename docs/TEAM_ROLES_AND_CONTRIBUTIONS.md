# SlopeGuard: Team Roles, Contributions & Responsibility Guide

> **Project Mission**: Deliver a production-grade, end-to-end Geospatial Landslide Early-Warning System (EWS) for high-risk mountainous terrains (North-Eastern Region of India) by bridging geotechnical research, machine learning inference, robust backend services, and interactive GIS decision-support dashboards.

---

## 1. Project High-Level Architecture & Workflow

SlopeGuard unites 4 core engineering disciplines into a cohesive pipeline:

```text
[Research & Data] ──> [ML Engineering] ──> [Backend Services] ──> [Streamlit UI / Ops]
  GSI / DEM / ERA5       Random Forest        FastAPI + PostGIS      Interactive GIS Map
  Spatial Split          Manifest & SHA       Alert State Machine    Simulators & Studio
```

---

## 2. Role-by-Role Breakdown

### 🔬 Role 1: Researcher / Domain Specialist (Geotechnical & Geospatial)

#### Core Purpose
Ground the system in real geological science, ensuring that landslide risk predictions reflect physical slope stability mechanics rather than arbitrary mathematical correlations.

#### Key Contributions & Deliverables
1. **Dataset Curation & Geological Grounding**:
   - Analyzed landslide records from the **Geological Survey of India (GSI)** for the North-Eastern Region (NER: Arunachal Pradesh, Papum Pare, Subansiri corridor).
   - Enriched raw records with digital elevation models (DEM) and ERA5 atmospheric reanalysis data.
2. **Feature Selection (8-Variable Physical Formulation)**:
   - Formulated the 8 critical geotechnical and meteorological parameters:
     - **Topographic**: Elevation (`Elevation_m`), Slope gradient (`Slope_deg`), Slope aspect (`Aspect_deg`).
     - **Geotechnical**: Soil clay percentage (`Soil_Clay_pct`), Soil sand percentage (`Soil_Sand_pct`).
     - **Hydrological**: Daily trigger rainfall (`Rainfall_mm`), 7-day cumulative antecedent rainfall (`Rainfall_7day_antecedent_mm`), and ERA5 regional event storm volume (`Rainfall_Event_ERA5_mm`).
3. **Rigorous Validation Methodology**:
   - Designed the **Spatial Group Holdout Validation** strategy using **0.25° grid cells (~27 km)**.
   - Prevented spatial autocorrelation data leakage (a fatal flaw in many academic models where adjacent points from the same hill slope appear in both train and test sets).
4. **Hazard & Exposure Buffer Standards**:
   - Defined the **2,000m critical hazard buffer zone** around watershed centroids based on debris-flow runout dynamics.

#### How to Present Your Contribution
> *"I ensured that SlopeGuard is scientifically sound. I selected the 8 geotechnical and meteorological drivers of slope failure, identified the GSI NER inventory, and designed a spatial block cross-validation scheme that eliminates geographic leakage, guaranteeing realistic real-world generalizability."*

---

### 🤖 Role 2: Machine Learning (ML) Engineer

#### Core Purpose
Transform research hypotheses and raw spatial data into an optimized, calibrated, explainable, and production-ready machine learning artifact.

#### Key Contributions & Deliverables
1. **Model Architecture & Training**:
   - Implemented and tuned an ensemble **Random Forest Classifier** (`RandomForestClassifier`) optimized for tabular geospatial features (`n_estimators=50`, `max_depth=8`, `class_weight='balanced'`).
   - Solved extreme positive-event class imbalance inherent in real-world landslide occurrences without artificial overfitting.
2. **Evaluation Metrics & Benchmarks**:
   - Achieved holdout validation performance of **0.7769 ROC-AUC**, **0.6229 PR-AUC**, and **68.9% accuracy** under rigorous spatial holdout splits.
   - Validated confusion matrix performance to prioritize disaster recall while minimizing false alarm rates.
3. **Artifact Integrity & Serialization Contract**:
   - Serialized the trained model bundle using `joblib` (`landslide_model.joblib`).
   - Created the automated cryptographic **`model_manifest.json`** specification containing feature schemas, statistical distribution medians (`p25`, `median`, `p75`), and a **SHA-256 integrity checksum** (`75560de7...`).
4. **Explainable AI (XAI) Driver Engine**:
   - Created transparent quantile-based feature attribution that returns human-readable risk drivers (e.g., *"High rainfall"*, *"Steep slope"*, *"High clay soil content"*) rather than black-box probability scores.

#### How to Present Your Contribution
> *"I built the production ML pipeline. I trained and tuned the balanced 8-variable Random Forest model, achieved 0.78 ROC-AUC on spatial holdout validation, secured the model with SHA-256 manifest integrity verification, and built explainable risk drivers that tell field operators exactly why a slope is at risk."*

---

### ⚙️ Role 3: Backend Engineer (API, Database & Alert Dispatch)

#### Core Purpose
Build the resilient, real-time backend microservices, database schemas, geospatial indexing, and multi-channel alerting infrastructure.

#### Key Contributions & Deliverables
1. **FastAPI Asynchronous Architecture**:
   - Engineered the asynchronous REST API with structured Pydantic v2 schemas (`PredictionRequest`, `AlertSummary`, `SimulationRun`, `TelemetryObservation`).
   - Built the decoupled `ArtifactModelGateway` adapter that safely executes synchronous ML inference inside non-blocking async routes.
2. **PostGIS Geospatial Engine**:
   - Implemented PostgreSQL with PostGIS extension for polygon watershed cells (`RiskCell`) and critical infrastructure points (`Asset`).
   - Engineered spatial SQL queries using `ST_DWithin`, `ST_Centroid`, `ST_X`, and `ST_Y` to calculate real-time asset exposure within the 2,000m radius.
3. **Alert Policy Engine & State Machine**:
   - Developed the 4-tier alert threshold evaluation (`LOW` < 0.40, `MEDIUM` 0.40-0.65, `HIGH` 0.65-0.80, `CRITICAL` ≥ 0.80).
   - Implemented the deterministic state machine (`ACTIVE` → `ACKNOWLEDGED` → `VERIFIED` → `RESOLVED`) with automatic risk escalation (`ESCALATED`).
   - Implemented a 30-minute deduplication cooldown to prevent notification fatigue.
4. **Multi-Channel Notification & Ingestion Queue**:
   - Built a real-time **WebSocket broadcast server** (`/ws/alerts`) for live dashboard push.
   - Built the **Firebase Cloud Messaging (FCM)** push notification client with exponential backoff and dead-letter pruning.
   - Implemented asynchronous telemetry observation ingestion using **APScheduler** background daemons with row-level transaction locks.

#### How to Present Your Contribution
> *"I architected the backend core. I integrated PostGIS for spatial 2km infrastructure exposure calculations, developed the stateful alert lifecycle engine with cooldown deduplication, and built the live WebSocket and FCM push notification pipeline to distribute warnings in milliseconds."*

---

### 💻 Role 4: Software Developer / Frontend Engineer (Streamlit GIS UI)

#### Core Purpose
Deliver an intuitive, high-performance, dark-mode geospatial command center that empowers emergency operators and decision-makers to visualize risks and take action.

#### Key Contributions & Deliverables
1. **Interactive Geospatial Command Center (Tab 1)**:
   - Integrated **Folium & Streamlit-Folium** to visualize watershed boundary polygons, color-coded risk levels (Green, Yellow, Orange, Red), and 2km critical asset exposure buffers.
   - Built an interactive cell inspector showing real-time terrain statistics, exposed facilities (hospitals, schools, highways), and responsive risk gauges.
2. **Interactive ML Prediction Studio (Tab 2)**:
   - Created a dynamic simulation studio with scenario presets (*Dry Season*, *Monsoon Downpour*, *Extreme Cloudburst*).
   - Designed real-time sliders for hydrological, soil, and topographical parameters with seamless direct model inference.
   - Added a modern circular buffering spinner during calculations to provide responsive visual feedback.
3. **Monsoon Rainfall Surge Simulator (Tab 3)**:
   - Engineered the rainfall surge multiplier sandbox (0.5x to 5.0x baseline) with dynamic Plotly tipping-point sensitivity curves.
   - Built simulated telemetry sensor ingestion controls with instant local feedback.
4. **Alert Lifecycle Operations Hub (Tab 4)**:
   - Built the incident stream management UI with status and severity filters.
   - Integrated operator workflow action buttons (`Acknowledge`, `Verify Field Report`, `Resolve Alert`) tied directly to backend state transitions.
5. **Model Transparency & Provenance Analytics (Tab 5)**:
   - Visualized the model specification, feature importances bar chart, holdout confusion matrix, and spatial grouping validation metrics from `model_manifest.json`.
6. **Dual-Mode Connectivity Architecture**:
   - Engineered the frontend `SlopeGuardClient` with automatic failover: seamlessly queries the live FastAPI backend, and falls back to direct in-memory ML model execution if the backend is offline.

#### How to Present Your Contribution
> *"I designed and developed the entire Streamlit decision-support dashboard. I built the interactive GIS map with Folium, the real-time ML prediction sandbox, the monsoon surge tipping-point simulator, and the operator alert incident management hub, complete with dual-mode offline/online fallback."*

---

### 🚀 Role 5: DevOps / Deployment & Integration Engineer

#### Core Purpose
Ensure reliable deployment, environment stability, container orchestration, and rapid packaging across cloud and local targets.

#### Key Contributions & Deliverables
1. **Streamlit Community Cloud Production Deployment**:
   - Configured repository structure, root and subfolder `requirements.txt`, and `.streamlit/config.toml` (headless mode, custom dark theme).
   - Resolved multi-environment Python 3.14/uv dependency resolution (Pydantic v2 schemas, Scikit-learn unpickle compatibility).
2. **Containerization & Local Orchestration**:
   - Built the multi-stage backend `Dockerfile` and `compose.yaml` spinning up FastAPI, PostgreSQL 16 with PostGIS 3.4, and volume mounts.
3. **Database Migrations & CI Test Automation**:
   - Configured **Alembic** migration chains and managed automated test suites across API routes and ML gateway contracts (`pytest`).

#### How to Present Your Contribution
> *"I managed the system infrastructure and cloud deployment. I containerized the services with Docker Compose and PostGIS, automated the test pipeline, and configured Streamlit Community Cloud for public zero-downtime deployment."*

---

## 3. Team Responsibility & Deliverables Matrix

| Discipline / Area | Responsible Role | Key Tech Stack | Primary Deliverables |
| :--- | :--- | :--- | :--- |
| **Geological & Terrain Research** | Researcher | GIS, DEM, ERA5, GSI | Feature formulation, 2km hazard buffer rule, spatial group split |
| **Machine Learning Model** | ML Engineer | Scikit-Learn, Joblib, Pandas | 8-variable Random Forest, `model_manifest.json`, driver explanations |
| **Backend API & Data Services** | Backend Engineer | FastAPI, Pydantic v2, Python | Async REST endpoints, ML model gateway adapter |
| **Spatial Database & Queries** | Backend Engineer | PostgreSQL, PostGIS, SQLAlchemy | Spatial tables (`RiskCell`, `Asset`), `ST_DWithin` exposure calculation |
| **Alert State Engine & Push** | Backend Engineer | WebSockets, FCM, APScheduler | Alert lifecycle machine, cooldown logic, telemetry queue |
| **Geospatial GIS Dashboard** | Frontend Developer | Streamlit, Folium, Plotly | Command map, live risk gauge, interactive cell inspector |
| **Simulation & Operator Hub** | Frontend Developer | Streamlit, Streamlit-Folium | Scenario presets, surge multiplier sandbox, incident stream |
| **DevOps & Cloud Deployment** | DevOps / Full Stack | Docker, Compose, UV, Streamlit Cloud | Live deployment (`slopeguard.streamlit.app`), container setup |

---

## 4. Key Cross-Team Interfaces & Handshakes

To explain how the team collaborated effectively, highlight these 3 clear integration contracts:

1. **Researcher ⟷ ML Engineer Handshake**:
   - The Researcher defined the 8 physical features and spatial group validation boundary (0.25° cells).
   - The ML Engineer trained and validated the Random Forest model to adhere strictly to these physical criteria.

2. **ML Engineer ⟷ Backend Engineer Handshake**:
   - The ML Engineer provided `landslide_model.joblib` and `model_manifest.json` with a SHA-256 hash.
   - The Backend Engineer built `ArtifactModelGateway` which validates the hash at startup and maps incoming API requests into the exact model feature vector.

3. **Backend Engineer ⟷ Frontend Developer Handshake**:
   - The Backend Engineer defined strict Pydantic v2 schemas and REST/WebSocket endpoints.
   - The Frontend Developer consumed these contracts in `SlopeGuardClient`, while providing an in-process fallback so the UI operates both with and without an active backend server.

---

## 5. Summary Cheat-Sheet for Team Presentations & Viva

When presenting to evaluators, professors, or stakeholders:
- **Researcher**: Emphasize **why** rainfall-only alerts fail and how geotechnical variables + spatial group splitting provide real-world accuracy.
- **ML Engineer**: Emphasize the **8-variable Random Forest**, the 0.78 ROC-AUC score, cryptographic manifest verification, and transparent drivers.
- **Backend Engineer**: Emphasize **PostGIS spatial exposure queries**, the alert state transition engine, and real-time WebSockets/FCM.
- **Frontend Developer**: Emphasize the **user experience**, interactive Folium GIS mapping, monsoon sensitivity curves, and operator action workflows.
