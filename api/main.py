from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path to import ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.model import ManRakshakAIEngine

app = FastAPI(title="ManRakshak AI API")

# Global variables to act as in-memory database and loaded model
engine = None
df_db = None

@app.on_event("startup")
async def startup_event():
    global engine, df_db
    try:
        engine = ManRakshakAIEngine()
        # Ensure we run from the project root
        model_path_exists = os.path.exists("ai_engine/models/calibrated_xgboost.pkl") or os.path.exists("models/calibrated_xgboost.pkl")
        
        if os.path.exists("ai_engine/models/calibrated_xgboost.pkl"):
             os.chdir("ai_engine")
             
        engine.load_model()
        print("AI Model loaded successfully.")
        
        data_path = "../synthetic_welfare_data.csv" if os.path.exists("../synthetic_welfare_data.csv") else "synthetic_welfare_data.csv"
        
        df_raw = pd.read_csv(data_path)
        # Precompute temporal features so they are ready for serving
        df_db = engine.generate_temporal_features(df_raw)
        print("In-memory database loaded.")
    except Exception as e:
        print(f"Startup error: {e}")

class WellnessCheckIn(BaseModel):
    sleep_hours: float
    mood_score: float
    workload_perception: float
    self_reported_stress: float
    
class WhatIfRequest(BaseModel):
    sleep_hours: float = None
    mood_score: float = None
    workload_perception: float = None
    night_duty: int = None

@app.get("/")
def read_root():
    return {"status": "ManRakshak API is running"}

def get_personnel_features(personnel_id: str):
    if df_db is None:
         raise HTTPException(status_code=503, detail="Database not loaded")
         
    p_data = df_db[df_db['personnel_id'] == personnel_id].sort_values(by='date')
    if p_data.empty:
        raise HTTPException(status_code=404, detail="Personnel not found")
        
    # Get the latest features
    latest_record = p_data.iloc[-1].to_dict()
    return latest_record

@app.post("/personnel/{personnel_id}/wellness")
def submit_wellness(personnel_id: str, checkin: WellnessCheckIn):
    # In a real app, this would save to the DB and recalculate baselines
    return {"status": "success", "message": "Wellness check-in recorded successfully"}

@app.get("/personnel/{personnel_id}/risk")
def get_risk(personnel_id: str):
    features = get_personnel_features(personnel_id)
    
    # Calculate risk
    try:
        risk_result = engine.predict_risk(features)
        
        # Add basic trend (comparing current risk to 7 days ago, but since we just have probabilities...)
        # We can simulate trend calculation for MVP
        trend = "Rising" if features['workload_deviation'] > 0 and features['sleep_deviation'] < 0 else "Stable"
        
        risk_result['trend'] = trend
        return risk_result
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/personnel/{personnel_id}/what-if")
def what_if_analysis(personnel_id: str, req: WhatIfRequest):
    features = get_personnel_features(personnel_id).copy()
    
    # Apply what-if overrides
    if req.sleep_hours is not None:
        features['sleep_hours'] = req.sleep_hours
        # Recalculate deviation based on baseline
        features['sleep_deviation'] = req.sleep_hours - features['sleep_baseline_7d']
        
    if req.mood_score is not None:
        features['mood_score'] = req.mood_score
        features['mood_deviation'] = req.mood_score - features['mood_baseline_7d']
        
    if req.workload_perception is not None:
        features['workload_perception'] = req.workload_perception
        features['workload_deviation'] = req.workload_perception - features['workload_baseline_7d']
        
    if req.night_duty is not None:
        features['night_duty'] = req.night_duty
        
    try:
        risk_result = engine.predict_risk(features)
        
        # Add recommendations based on new risk profile
        recommendations = []
        if risk_result['risk_probability'] > 0.6:
            recommendations.append("Workload review")
            recommendations.append("Recovery support")
        elif risk_result['risk_probability'] > 0.4:
            recommendations.append("Wellness follow-up")
            
        risk_result['recommendations'] = recommendations
        
        return {
            "scenario": "What-If Analysis",
            "predicted_risk": risk_result
        }
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/welfare")
def welfare_dashboard():
    # Return aggregate elevated cases
    if df_db is None:
         return {"error": "DB not loaded"}
         
    # Get latest records for all personnel
    latest_df = df_db.sort_values('date').groupby('personnel_id').tail(1)
    
    # Calculate simple stats
    total_personnel = len(latest_df)
    
    # We would ideally run the model on all of them, but for MVP speed, we'll use the synthetic risk_flag
    elevated_cases = len(latest_df[latest_df['risk_flag'] == 1])
    
    return {
        "total_personnel": total_personnel,
        "elevated_cases": elevated_cases,
        "follow_ups_needed": int(elevated_cases * 0.4), # Simulated
        "top_factors_overall": ["Sleep", "Workload", "Duty Pattern"]
    }

@app.get("/dashboard/commander")
def commander_dashboard():
    # Aggregate info only
    return {
        "unit_wellness": {
            "stress_trend": "+12%",
            "workload_trend": "+8%",
            "fatigue_trend": "+5%"
        },
        "high_pressure_periods": ["Week 2", "Week 4"],
        "recommendations": [
            "Review duty distribution",
            "Increase welfare availability"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
