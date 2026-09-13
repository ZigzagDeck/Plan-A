"""API and ML Integration Client for SlopeGuard Streamlit Dashboard.
Handles REST requests to FastAPI and provides direct access to the real
Random Forest ML model artifact.
"""

import asyncio
import json
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[2] / "backend"
import sys
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
MODEL_PATH = BACKEND_DIR / "app" / "model_artifacts" / "landslide_model.joblib"
MANIFEST_PATH = BACKEND_DIR / "app" / "model_artifacts" / "model_manifest.json"

DEFAULT_API_URL = "http://127.0.0.1:8000"

# Standard North-Eastern Region Landslide Risk Cells (Papum Pare & Subansiri, Arunachal Pradesh)
SAMPLE_CELLS = [

    {
        "cell_code": "NER-CELL-A17",
        "name": "Papum Pare Hill Section",
        "latitude": 27.15,
        "longitude": 93.75,
        "elevation_m": 820.0,
        "slope_deg": 42.5,
        "aspect_deg": 145.0,
        "baseline_rainfall_mm": 45.0,
        "polygon": [
            [27.10, 93.70],
            [27.10, 93.80],
            [27.20, 93.80],
            [27.20, 93.70],
        ],
    },
    {
        "cell_code": "NER-CELL-B04",
        "name": "Lower Subansiri Escarpment",
        "latitude": 27.30,
        "longitude": 93.90,
        "elevation_m": 1150.0,
        "slope_deg": 48.0,
        "aspect_deg": 210.0,
        "baseline_rainfall_mm": 85.0,
        "polygon": [
            [27.25, 93.85],
            [27.25, 93.95],
            [27.35, 93.95],
            [27.35, 93.85],
        ],
    },
    {
        "cell_code": "NER-CELL-C12",
        "name": "Kameng Valley Slope",
        "latitude": 27.05,
        "longitude": 93.55,
        "elevation_m": 450.0,
        "slope_deg": 24.0,
        "aspect_deg": 85.0,
        "baseline_rainfall_mm": 20.0,
        "polygon": [
            [27.00, 93.50],
            [27.00, 93.60],
            [27.10, 93.60],
            [27.10, 93.50],
        ],
    },
    {
        "cell_code": "NER-CELL-D08",
        "name": "Itanagar Urban Ridge",
        "latitude": 27.10,
        "longitude": 93.65,
        "elevation_m": 720.0,
        "slope_deg": 36.5,
        "aspect_deg": 175.0,
        "baseline_rainfall_mm": 60.0,
        "polygon": [
            [27.05, 93.60],
            [27.05, 93.70],
            [27.15, 93.70],
            [27.15, 93.60],
        ],
    },
]

SAMPLE_ASSETS = [
    {
        "asset_code": "AST-SCH-01",
        "type": "SCHOOL",
        "name": "Papum Pare District High School",
        "latitude": 27.14,
        "longitude": 93.74,
        "cell_code": "NER-CELL-A17",
    },
    {
        "asset_code": "AST-HSP-01",
        "type": "HOSPITAL",
        "name": "Sub-divisional Medical Center",
        "latitude": 27.16,
        "longitude": 93.76,
        "cell_code": "NER-CELL-A17",
    },
    {
        "asset_code": "AST-RD-NH13",
        "type": "ROAD",
        "name": "National Highway NH-13 Corridor",
        "latitude": 27.15,
        "longitude": 93.75,
        "cell_code": "NER-CELL-A17",
    },
    {
        "asset_code": "AST-BRG-03",
        "type": "BRIDGE",
        "name": "Dikrong River Bridge",
        "latitude": 27.12,
        "longitude": 93.72,
        "cell_code": "NER-CELL-A17",
    },
    {
        "asset_code": "AST-PWR-02",
        "type": "POWER",
        "name": "Itanagar Main Substation",
        "latitude": 27.09,
        "longitude": 93.65,
        "cell_code": "NER-CELL-D08",
    },
    {
        "asset_code": "AST-COM-01",
        "type": "COMMUNICATION",
        "name": "Doordarshan Microwave Tower",
        "latitude": 27.29,
        "longitude": 93.88,
        "cell_code": "NER-CELL-B04",
    },
]


class SlopeGuardClient:
    """Synchronous & async client with real ML artifact fallback."""

    def __init__(self, base_url: str = DEFAULT_API_URL):
        self.base_url = base_url.rstrip("/")
        self._gateway = None

    def _get_ml_gateway(self):
        """Lazy load the actual ArtifactModelGateway directly from backend module."""
        if self._gateway is None:
            import sys

            if str(BACKEND_DIR) not in sys.path:
                sys.path.insert(0, str(BACKEND_DIR))
            from app.services.model_gateway import ArtifactModelGateway

            self._gateway = ArtifactModelGateway(MODEL_PATH, MANIFEST_PATH)
        return self._gateway

    def load_manifest(self) -> dict[str, Any]:
        """Loads and returns the model_manifest.json."""
        if MANIFEST_PATH.is_file():
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        return {}

    def check_health(self) -> dict[str, Any]:
        """Checks liveness of the backend."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.base_url}/health")
                if res.status_code == 200:
                    return {"online": True, "data": res.json()}
        except Exception:
            pass
        return {"online": False, "data": None}

    def direct_predict(
        self,
        latitude: float,
        longitude: float,
        elevation_m: float,
        slope_deg: float,
        aspect_deg: float,
        rainfall_mm: float,
        rainfall_7day_antecedent_mm: float | None = None,
        rainfall_event_era5_mm: float | None = None,
        soil_clay_pct: float | None = None,
        soil_sand_pct: float | None = None,
    ) -> dict[str, Any]:
        """Performs inference directly using the trained Random Forest model."""
        import sys

        if str(BACKEND_DIR) not in sys.path:
            sys.path.insert(0, str(BACKEND_DIR))
        from app.schemas.prediction import ModelFeatures

        features = ModelFeatures(
            latitude=latitude,
            longitude=longitude,
            elevation_m=elevation_m,
            slope_deg=slope_deg,
            aspect_deg=aspect_deg,
            rainfall_mm=rainfall_mm,
            rainfall_7day_antecedent_mm=rainfall_7day_antecedent_mm,
            rainfall_event_era5_mm=rainfall_event_era5_mm,
            soil_clay_pct=soil_clay_pct,
            soil_sand_pct=soil_sand_pct,
        )
        gateway = self._get_ml_gateway()
        prediction = asyncio.run(gateway.predict(features))

        prob = prediction.probability
        # Risk level determination based on config thresholds (0.40, 0.65, 0.80)
        if prob >= 0.80:
            level = "CRITICAL"
        elif prob >= 0.65:
            level = "HIGH"
        elif prob >= 0.40:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "probability": prob,
            "predicted_class": prediction.predicted_class,
            "risk_level": level,
            "drivers": prediction.drivers,
            "method": "Direct Random Forest Artifact",
        }

    def predict_via_api(
        self,
        cell_code: str,
        rainfall_mm: float,
        rainfall_7day: float | None = None,
        rainfall_era5: float | None = None,
        soil_clay: float | None = None,
        soil_sand: float | None = None,
    ) -> dict[str, Any]:
        """Calls POST /api/v1/predict on the backend, falling back to direct ML inference."""
        payload = {
            "cell_code": cell_code,
            "rainfall_mm": rainfall_mm,
            "rainfall_7day_antecedent_mm": rainfall_7day,
            "rainfall_event_era5_mm": rainfall_era5,
            "soil_clay_pct": soil_clay,
            "soil_sand_pct": soil_sand,
        }
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.post(f"{self.base_url}/api/v1/predict", json=payload)
                if res.status_code == 201:
                    data = res.json()
                    data["method"] = "Backend API (/api/v1/predict)"
                    return data
        except Exception:
            pass

        # Fallback to direct model inference using matching sample cell features
        cell = next((c for c in SAMPLE_CELLS if c["cell_code"] == cell_code), SAMPLE_CELLS[0])
        result = self.direct_predict(
            latitude=cell["latitude"],
            longitude=cell["longitude"],
            elevation_m=cell["elevation_m"],
            slope_deg=cell["slope_deg"],
            aspect_deg=cell["aspect_deg"],
            rainfall_mm=rainfall_mm,
            rainfall_7day_antecedent_mm=rainfall_7day,
            rainfall_event_era5_mm=rainfall_era5,
            soil_clay_pct=soil_clay,
            soil_sand_pct=soil_sand,
        )
        result["cell_code"] = cell_code
        result["rainfall_mm"] = rainfall_mm
        result["snapshot_id"] = str(uuid4())
        return result

    def simulate_rainfall(
        self,
        cell_code: str,
        rainfall_multiplier: float,
        baseline_rainfall_mm: float | None = None,
        rainfall_7day: float | None = None,
        rainfall_era5: float | None = None,
        soil_clay: float | None = None,
        soil_sand: float | None = None,
    ) -> dict[str, Any]:
        """Calls POST /api/v1/simulation/rainfall or computes simulated surge."""
        payload = {
            "cell_code": cell_code,
            "rainfall_multiplier": rainfall_multiplier,
            "baseline_rainfall_mm": baseline_rainfall_mm,
            "rainfall_7day_antecedent_mm": rainfall_7day,
            "rainfall_event_era5_mm": rainfall_era5,
            "soil_clay_pct": soil_clay,
            "soil_sand_pct": soil_sand,
        }
        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.post(f"{self.base_url}/api/v1/simulation/rainfall", json=payload)
                if res.status_code == 201:
                    return res.json()
        except Exception:
            pass

        # Standalone computation fallback
        cell = next((c for c in SAMPLE_CELLS if c["cell_code"] == cell_code), SAMPLE_CELLS[0])
        baseline = baseline_rainfall_mm or cell["baseline_rainfall_mm"]
        simulated_rainfall = round(baseline * rainfall_multiplier, 2)
        prediction = self.direct_predict(
            latitude=cell["latitude"],
            longitude=cell["longitude"],
            elevation_m=cell["elevation_m"],
            slope_deg=cell["slope_deg"],
            aspect_deg=cell["aspect_deg"],
            rainfall_mm=simulated_rainfall,
            rainfall_7day_antecedent_mm=rainfall_7day,
            rainfall_event_era5_mm=rainfall_era5,
            soil_clay_pct=soil_clay,
            soil_sand_pct=soil_sand,
        )
        return {
            "simulation_id": str(uuid4()),
            "cell_code": cell_code,
            "baseline_rainfall_mm": baseline,
            "rainfall_multiplier": rainfall_multiplier,
            "simulated_rainfall_mm": simulated_rainfall,
            "prediction": prediction,
        }

    def list_alerts(self, status: str | None = None, severity: str | None = None) -> list[dict]:
        """Calls GET /api/v1/alerts."""
        try:
            params = {}
            if status:
                params["status"] = status
            if severity:
                params["severity"] = severity
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/v1/alerts", params=params)
                if res.status_code == 200:
                    return res.json().get("items", [])
        except Exception:
            pass
        return []

    def transition_alert(
        self,
        alert_id: str,
        action: str,  # "acknowledge", "verify", "resolve"
        author: str,
        reason: str,
    ) -> dict[str, Any]:
        """Calls POST /api/v1/alerts/{alert_id}/{action}."""
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.post(
                    f"{self.base_url}/api/v1/alerts/{alert_id}/{action}",
                    json={"author": author, "reason": reason},
                )
                if res.status_code == 200:
                    return {"success": True, "data": res.json()}
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def enqueue_observation(
        self,
        cell_code: str,
        rainfall_mm: float,
        source: str = "field-telemetry",
    ) -> dict[str, Any]:
        """Calls POST /api/v1/rainfall/observations."""
        import datetime

        payload = {
            "source": source,
            "source_event_id": f"evt-{uuid4().hex[:8]}",
            "cell_code": cell_code,
            "rainfall_mm": rainfall_mm,
            "observed_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.post(f"{self.base_url}/api/v1/rainfall/observations", json=payload)
                if res.status_code == 202:
                    return {"success": True, "data": res.json()}
                return {"success": False, "error": res.text}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Backward compatibility alias
PlanAClient = SlopeGuardClient

