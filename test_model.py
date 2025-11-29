import pandas as pd
import numpy as np
from synthetic_data import generate_time_series_data
from lstm_model import train_model, predict_next

def test_lstm_pipeline():
    print("Generating synthetic data...")
    locations = ["Test Loc"]
    df = generate_time_series_data(locations, days=50)
    print(f"Data generated: {len(df)} rows.")
    print(df.head())

    print("\nTraining model...")
    model, scaler_params = train_model(df, "Test Loc", epochs=50)
    
    if model:
        print("Model trained successfully.")
        
        # Test prediction
        recent_data = df['Threat_Level'].values[-5:]
        print(f"Recent data: {recent_data}")
        
        prediction = predict_next(model, recent_data, scaler_params)
        print(f"Predicted next threat level: {prediction}")
    else:
        print("Model training failed (likely insufficient data).")

if __name__ == "__main__":
    test_lstm_pipeline()
