from fastapi import FastAPI, HTTPException, Body
from .models import LoginRequest, SMSRequest, CattleParams, PredictionRequest, WebhookRequest
from . import logic, synthetic_data, lstm_model
from typing import List, Dict
import pandas as pd
import numpy as np

app = FastAPI(title="Ulinzi API")

# Global state for models (Hackathon style)
lstm_models = {}
lstm_scalers = {}
iso_forest_model = logic.train_isolation_forest()

@app.get("/")
def read_root():
    return {"status": "online", "system": "Ulinzi Backend"}

# --- Auth ---
@app.post("/auth/login")
def login(creds: LoginRequest):
    if creds.username == "admin" and creds.password == "niruhack123":
        return {"authenticated": True, "token": "ulinzi-hack-token"}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# --- SMS ---
@app.post("/sms/send")
def send_sms(req: SMSRequest, api_key: str, device_id: str):
    success, resp = logic.send_alert_sms(api_key, device_id, req.recipients, req.message)
    if success:
        return {"status": "success", "response": resp}
    else:
        raise HTTPException(status_code=500, detail=resp)

@app.get("/sms/check")
def check_sms(api_key: str, device_id: str, sender_phone: str, min_timestamp: str = None):
    # sender_phone can be comma separated
    phones = [p.strip() for p in sender_phone.split(",")]
    
    ts = None
    if min_timestamp:
        try:
            ts = pd.to_datetime(min_timestamp)
        except:
            pass
            
    found, result, debug = logic.check_for_sms_reply(api_key, device_id, phones, ts)
    return {"found": found, "result": result, "debug": debug}

@app.post("/alerts/n8n")
def trigger_n8n(req: WebhookRequest):
    success, msg = logic.trigger_n8n_webhook(req.webhook_url, {"message": req.message, "data": req.data})
    if success:
        return {"status": "success", "message": msg}
    else:
        raise HTTPException(status_code=500, detail=msg)

# --- Cattle Data (GrazingGuard) ---
@app.post("/cattle/data")
def get_cattle_data(params: CattleParams):
    df = logic.get_cattle_data(
        mode=params.mode,
        num_cows=params.num_cows,
        center_lat=params.center_lat,
        center_lon=params.center_lon
    )
    # Convert to list of dicts for JSON
    return df.to_dict(orient="records")

@app.post("/cattle/predict")
def predict_cattle_threat(data: List[Dict]):
    df = pd.DataFrame(data)
    if df.empty:
        return []
    
    features = df[['speed_kmh', 'hour_of_day']]
    scores = iso_forest_model.predict(features)
    
    # Hybrid detection: AI + Rule-based fallback
    status = []
    for i, s in enumerate(scores):
        speed = df.iloc[i]['speed_kmh']
        hour = df.iloc[i]['hour_of_day']
        
        # Use AI prediction OR rule-based detection
        if s == -1 or logic.detect_raid_with_rules(speed, hour):
            status.append("THREAT DETECTED")
        else:
            status.append("Safe")
    
    return status

# --- History Data (Regional Dashboard) ---
@app.get("/history/data")
def get_history_data(locations: str, days: int = 60):
    loc_list = locations.split(",")
    df = synthetic_data.generate_time_series_data(loc_list, days)
    # Convert dates to string for JSON
    df['Date'] = df['Date'].astype(str)
    return df.to_dict(orient="records")

@app.post("/history/train")
def train_history_model(data: List[Dict], location: str):
    df = pd.DataFrame(data)
    df['Date'] = pd.to_datetime(df['Date'])
    
    model, scaler = lstm_model.train_model(df, location, epochs=20) # Lower epochs for speed
    if model:
        lstm_models[location] = model
        lstm_scalers[location] = scaler
        return {"status": "trained"}
    else:
        return {"status": "failed"}

@app.post("/history/predict")
def predict_history(location: str, recent_data: List[float]):
    if location not in lstm_models:
        raise HTTPException(status_code=404, detail="Model not trained for this location")
    
    model = lstm_models[location]
    scaler = lstm_scalers[location]
    
    prediction = lstm_model.predict_next(model, np.array(recent_data), scaler)
    return {"prediction": prediction}
