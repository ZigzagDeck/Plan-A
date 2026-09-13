from fastapi import FastAPI
import joblib
import numpy as np
from pydantic import BaseModel

app = FastAPI(title="Plan-A ML Inference API")

# Load the trained machine learning model and feature names
# Isko aise update kar do:
model = joblib.load("ml/artifacts/landslide_model.pkl")
feature_names = joblib.load("ml/artifacts/feature_names.pkl")

class PredictionRequest(BaseModel):
    Elevation_m: float
    Slope_deg: float
    Aspect_deg: float
    Rainfall_mm: float
    Rainfall_7day_antecedent_mm: float
    Rainfall_Event_ERA5_mm: float
    Soil_Clay_pct: float
    Soil_Sand_pct: float

@app.post("/predict")
def predict_landslide(data: PredictionRequest):
    # Prepare input data array in the exact feature order
    input_data = np.array([[
        data.Elevation_m,
        data.Slope_deg,
        data.Aspect_deg,
        data.Rainfall_mm,
        data.Rainfall_7day_antecedent_mm,
        data.Rainfall_Event_ERA5_mm,
        data.Soil_Clay_pct,
        data.Soil_Sand_pct
    ]])
    
    # Predict probability and class
    prob = float(model.predict_proba(input_data)[0][1])
    pred_class = int(model.predict(input_data)[0])
    
    # Generate dynamic drivers based on threshold checks
    drivers = []
    if data.Rainfall_mm > 70 or data.Rainfall_Event_ERA5_mm > 40:
        drivers.append("High rainfall")
    if data.Slope_deg > 20:
        drivers.append("Steep slope")
    if data.Elevation_m > 1500:
        drivers.append("High elevation")
    if data.Rainfall_7day_antecedent_mm > 30:
        drivers.append("High antecedent rainfall")
    if data.Soil_Clay_pct > 30:
        drivers.append("High clay soil content")
        
    response = {
        "probability": round(prob, 2),
        "predicted_class": pred_class
    }
    
    if drivers:
        response["drivers"] = drivers
        
    return response