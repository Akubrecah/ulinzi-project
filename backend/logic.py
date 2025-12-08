import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import requests
from datetime import datetime

# --- SMS CONFIGURATION (TextBee) ---
def send_alert_sms(api_key, device_id, recipients, message):
    if not api_key or not device_id:
        return False, "Missing API Key or Device ID"

    url = f"https://api.textbee.dev/api/v1/gateway/devices/{device_id}/send-sms"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # TextBee expects an array of recipients
    # Ensure recipients is a list
    if isinstance(recipients, str):
        recipients = [recipients]
        
    payload = {
        "recipients": recipients,
        "message": message
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json()
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def check_for_sms_reply(api_key, device_id, sender_phone, min_timestamp=None):
    if not api_key or not device_id:
        return False, "Missing Credentials", None
        
    url = f"https://api.textbee.dev/api/v1/gateway/devices/{device_id}/get-received-sms"
    headers = {"x-api-key": api_key}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            messages = data.get('data', [])
            
            # DEBUG: Return the raw messages to see what's happening
            debug_info = [f"[{m.get('receivedAt')}] {m.get('sender')}: {m.get('message')}" for m in messages[:5]]
            
            target_nums = []
            if isinstance(sender_phone, list):
                target_nums = [n.replace("+", "").replace(" ", "")[-9:] for n in sender_phone]
            else:
                target_nums = [sender_phone.replace("+", "").replace(" ", "")[-9:]]

            for msg in messages:
                msg_sender = str(msg.get('sender', '')).replace("+", "").replace(" ", "")
                msg_body = str(msg.get('message', '')).upper()
                msg_time_str = msg.get('receivedAt')
                
                # Parse timestamp
                try:
                    # Handle ISO format with Z
                    msg_time = datetime.fromisoformat(msg_time_str.replace("Z", "+00:00"))
                except:
                    continue # Skip if invalid time format

                # Check if message is newer than the alert
                if min_timestamp and msg_time <= min_timestamp:
                    continue

                # Check if sender matches any target and body has keywords
                sender_match = False
                for t_num in target_nums:
                    if t_num in msg_sender or msg_sender in t_num:
                        sender_match = True
                        break
                
                if sender_match:
                    if any(keyword in msg_body for keyword in ["YES", "CONFIRM", "OK", "RAID", "APPROVED"]):
                        return True, msg.get('message'), debug_info
            return False, "No new matching reply found.", debug_info
        else:
            return False, f"API Error: {response.text}", None
    except Exception as e:
        return False, str(e), None

# --- 1. THE DATA SIMULATOR (Generating the Identity) ---
def get_cattle_data(mode="Normal", num_cows=50, center_lat=1.433, center_lon=35.115):
    # Use dynamic center coordinates
    base_lat = center_lat
    base_lon = center_lon
    
    if mode == "Normal":
        # Cows grazing: Slow speed, random clustered movement, Day time
        lat_noise = np.random.normal(0, 0.002, num_cows)
        lon_noise = np.random.normal(0, 0.002, num_cows)
        speed = np.random.uniform(0.5, 3.0, num_cows) # km/h
        hour = 14 # 2:00 PM
        
    else: # RAID MODE
        # Cows being stolen: Fast speed, linear directional movement, Night time
        # Moving fast towards a border (vector movement)
        lat_noise = np.random.normal(0.02, 0.005, num_cows) # Shifted location
        lon_noise = np.random.normal(0.02, 0.005, num_cows)
        speed = np.random.uniform(12.0, 18.0, num_cows) # Fast running
        hour = 2 # 2:00 AM
    
    df = pd.DataFrame({
        'lat': base_lat + lat_noise,
        'lon': base_lon + lon_noise,
        'speed_kmh': speed,
        'hour_of_day': [hour] * num_cows,
        'id': range(num_cows)
    })
    return df

# --- 2. THE AI MODEL (The Brain) ---
def train_isolation_forest():
    # Train on "Normal" grazing patterns
    # Features: Speed and Hour of Day (Simple Identity Signature)
    normal_data = get_cattle_data("Normal", num_cows=500, center_lat=0, center_lon=0) # Lat/Lon don't matter for training
    X_train = normal_data[['speed_kmh', 'hour_of_day']]
    
    # Increased contamination to 5% for better sensitivity
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_train)
    return model

def detect_raid_with_rules(speed, hour):
    """
    Rule-based fallback for raid detection.
    Returns True if characteristics match a raid pattern.
    """
    # Raid signature: High speed (>10 km/h) during night hours (midnight to 6 AM)
    if speed > 10.0 and (hour >= 0 and hour <= 6):
        return True
    return False

def trigger_n8n_webhook(webhook_url, data):
    """
    Sends a JSON payload to an n8n webhook via POST request.
    """
    if not webhook_url:
        return False, "No Webhook URL provided"
        
    try:
        # Extract and structure data for n8n
        chat_id = data.get("data", {}).get("chatId", "123456789")
        message = data.get("message", "")
        region = data.get("data", {}).get("region", "Unknown")
        threat_level = data.get("data", {}).get("threat_level", "MEDIUM")
        timestamp = data.get("data", {}).get("timestamp", "")
        
        # Build JSON payload
        payload = {
            "chatId": chat_id,
            "message": message,
            "region": region,
            "threat_level": threat_level,
            "timestamp": timestamp
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        if response.status_code == 200:
            return True, "Webhook triggered successfully"
        else:
            return False, f"Webhook failed with status {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

