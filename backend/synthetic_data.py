import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_time_series_data(locations, days=30):
    """
    Generates synthetic historical data for the given locations.
    Returns a DataFrame with columns: ['Date', 'Location', 'Threat_Level', 'Incident_Count']
    """
    data = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    for location in locations:
        # Simulate a trend for each location
        # Random base threat level between 1 and 4
        base_threat = np.random.randint(1, 5) 
        
        current_date = start_date
        while current_date <= end_date:
            # Add some random noise and seasonality
            noise = np.random.normal(0, 0.5)
            # Weekly seasonality (higher on weekends maybe? just random sine wave here)
            seasonality = np.sin(current_date.weekday() * (2 * np.pi / 7)) * 0.5
            
            threat_val = base_threat + noise + seasonality
            threat_val = max(1, min(5, round(threat_val))) # Clamp between 1 and 5
            
            # Incident count correlated with threat level
            incident_count = max(0, int(np.random.poisson(threat_val * 2)))
            
            data.append({
                'Date': current_date.strftime('%Y-%m-%d'),
                'Location': location,
                'Threat_Level': int(threat_val),
                'Incident_Count': incident_count
            })
            current_date += timedelta(days=1)
            
    return pd.DataFrame(data)

def generate_live_update(locations):
    """
    Generates a single day's worth of data for 'live' updates.
    """
    data = []
    today = datetime.now().strftime('%Y-%m-%d')
    
    for location in locations:
        threat_val = np.random.randint(1, 6)
        incident_count = np.random.randint(0, 10)
        
        data.append({
            'Date': today,
            'Location': location,
            'Threat_Level': threat_val,
            'Incident_Count': incident_count
        })
    return pd.DataFrame(data)
