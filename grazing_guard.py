import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
import time
import requests
import json

# --- SMS CONFIGURATION (TextBee) ---
def send_alert_sms(api_key, device_id, phone_number, message):
    if not api_key or not device_id:
        return False, "Missing API Key or Device ID"

    url = f"https://api.textbee.dev/api/v1/gateway/devices/{device_id}/send-sms"
    
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    # TextBee expects an array of recipients
    payload = {
        "recipients": [phone_number],
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

from datetime import datetime, timezone

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
            
            # Look for recent messages from the sender
            target_num = sender_phone.replace("+", "").replace(" ", "")[-9:] # Last 9 digits
            
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

                # Check if sender matches and body has keywords
                if target_num in msg_sender or msg_sender in target_num:
                    if any(keyword in msg_body for keyword in ["YES", "CONFIRM", "OK", "RAID", "APPROVED"]):
                        return True, msg.get('message'), debug_info
            return False, "No new matching reply found.", debug_info
        else:
            return False, f"API Error: {response.text}", None
    except Exception as e:
        return False, str(e), None

# --- 1. THE DATA SIMULATOR (Generating the Identity) ---
def get_cattle_data(mode="Normal", num_cows=50):
    # Base coordinates for West Pokot, Kenya
    base_lat = 1.433
    base_lon = 35.115
    
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
@st.cache_resource
def train_model():
    # Train on "Normal" grazing patterns
    # Features: Speed and Hour of Day (Simple Identity Signature)
    normal_data = get_cattle_data("Normal", num_cows=500)
    X_train = normal_data[['speed_kmh', 'hour_of_day']]
    
    # Contamination = 1% (We expect raids to be rare anomalies)
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X_train)
    return model

def render_grazing_guard():
    # --- 3. STREAMLIT DASHBOARD UI ---
    st.title("🛡️ GrazingGuard - Cattle Tracking")
    
    # Initialize Session State for Workflow
    if 'incident_state' not in st.session_state:
        st.session_state.incident_state = "MONITORING" # MONITORING, THREAT_DETECTED, WAITING_FOR_CHIEF, DISPATCHED
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    if 'alert_sent_time' not in st.session_state:
        st.session_state.alert_sent_time = None

    def add_log(message, type="info"):
        timestamp = time.strftime("%H:%M:%S")
        st.session_state.log_messages.insert(0, {"time": timestamp, "msg": message, "type": type})

    # Sidebar Controls (Local to this module)
    st.sidebar.markdown("---")
    st.sidebar.subheader("GrazingGuard Simulation")
    
    # SMS Settings
    st.sidebar.markdown("### 📲 TextBee Settings")
    # Hardcoded credentials as requested to hide them from UI
    TEXTBEE_API_KEY = "901124e8-7fca-4468-85a8-075ef29dd819"
    TEXTBEE_DEVICE_ID = "69312c2dd3fdd9bd6c54dfc7"
    
    elder_phone = st.sidebar.text_input("Elder Phone Number:", value="+254719299900", help="Verified number for testing")
    
    sim_mode = st.sidebar.radio("Herd Activity State:", ["Normal Grazing", "Active Raid Simulation"])

    # Reset state if simulation mode changes to Normal
    if sim_mode == "Normal Grazing" and st.session_state.incident_state != "MONITORING":
        st.session_state.incident_state = "MONITORING"
        st.session_state.log_messages = []

    # Generate Live Data based on selection
    live_data = get_cattle_data("Normal" if sim_mode == "Normal Grazing" else "Raid")
    model = train_model()

    # Run AI Prediction
    features = live_data[['speed_kmh', 'hour_of_day']]
    live_data['anomaly_score'] = model.predict(features)
    live_data['status'] = live_data['anomaly_score'].apply(lambda x: 'Safe' if x == 1 else 'THREAT DETECTED')
    
    # Detect if ANY cow is showing raid identity
    raid_detected = -1 in live_data['anomaly_score'].values
    
    if raid_detected and st.session_state.incident_state == "MONITORING":
        st.session_state.incident_state = "THREAT_DETECTED"
        add_log("AI detected anomalous grazing pattern (High Velocity Vector)", "error")

    # --- MAIN LAYOUT ---
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📍 Live Geospatial Tracking (West Pokot Sector 4)")
        
        # Using Plotly for the Map
        fig = px.scatter_mapbox(
            live_data, 
            lat="lat", 
            lon="lon", 
            color="status",
            color_discrete_map={"Safe": "#00CC96", "THREAT DETECTED": "#EF553B"},
            zoom=12, 
            height=500,
            size="speed_kmh", # Faster cows appear larger
            hover_data=["speed_kmh", "id"]
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📡 Command Center")
        
        # Metrics Row
        m1, m2 = st.columns(2)
        avg_speed = live_data['speed_kmh'].mean()
        m1.metric("Avg Speed", f"{avg_speed:.1f} km/h", delta="Normal" if avg_speed < 5 else "High", delta_color="inverse")
        
        current_hour = live_data['hour_of_day'].iloc[0]
        m2.metric("Time", f"{current_hour}:00 hrs")

        st.divider()
        
        # --- WORKFLOW STATE MACHINE ---
        
        if st.session_state.incident_state == "MONITORING":
            st.success("✅ System Status: MONITORING")
            st.caption("No anomalies detected in current grazing patterns.")
            
        elif st.session_state.incident_state == "THREAT_DETECTED":
            st.error("🚨 THREAT DETECTED")
            st.markdown("**AI Signature:** High Velocity (>12km/h) at 02:00 hrs.")
            
            st.warning("Action Required: Verify with Area Chief")
            
            if st.button("📲 Send SMS Alert to Chief"):
                if elder_phone:
                    with st.spinner("Sending SMS via TextBee..."):
                        msg = "ULINZI ALERT: Suspected Raid in Sector 4. Please CONFIRM status immediately."
                        success, resp = send_alert_sms(TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID, elder_phone, msg)
                        if success:
                            st.session_state.incident_state = "WAITING_FOR_CHIEF"
                            st.session_state.alert_sent_time = datetime.now(timezone.utc)
                            add_log(f"SMS Alert sent to Chief ({elder_phone})", "warning")
                            st.rerun()
                        else:
                            st.error(f"SMS Failed: {resp}")
                else:
                    st.error("Please enter Phone Number.")

        elif st.session_state.incident_state == "WAITING_FOR_CHIEF":
            st.info("⏳ Waiting for Chief's Confirmation...")
            st.caption("Please wait for the Chief to reply or call back.")
            
            with st.status("Verification in Progress", expanded=True):
                st.write("SMS Status: Sent ✅")
                st.write("Awaiting feedback...")
                
                c1, c2 = st.columns(2)
                if c1.button("✅ Chief Confirmed: RAID"):
                    st.session_state.incident_state = "READY_TO_DISPATCH"
                    add_log("Chief confirmed raid activity via phone.", "error")
                    st.rerun()
                
                if c2.button("❌ False Alarm"):
                    st.session_state.incident_state = "MONITORING"
                    add_log("Chief marked as False Alarm.", "success")
                    st.rerun()
                
                st.markdown("---")
                
                # Auto-Polling Logic
                st.write("🔄 **Live Status:** Listening for reply...")
                
                # Perform the check
                found, result, debug_msgs = check_for_sms_reply(TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID, elder_phone, st.session_state.alert_sent_time)
                
                if found:
                    st.success(f"📩 Reply Received: '{result}'")
                    st.session_state.incident_state = "READY_TO_DISPATCH"
                    add_log(f"Chief replied via SMS: {result}", "error")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    # Show debug info in an expander (collapsed by default)
                    with st.expander("Debug: Incoming Messages"):
                        if debug_msgs:
                            for m in debug_msgs:
                                st.write(m)
                        else:
                            st.write("No messages fetched.")
                    
                    # Wait and Rerun to create a polling loop
                    time.sleep(5)
                    st.rerun()

        elif st.session_state.incident_state == "READY_TO_DISPATCH":
            st.error("⚠️ RAID CONFIRMED - AUTHORIZED TO DISPATCH")
            
            if st.button("🚓 DISPATCH POLICE UNITS", type="primary", use_container_width=True):
                st.session_state.incident_state = "DISPATCHED"
                add_log("ASTU Unit dispatched to Sector 4.", "error")
                st.rerun()

        elif st.session_state.incident_state == "DISPATCHED":
            st.success("🚀 RESPONSE IN PROGRESS")
            st.markdown("### 🚓 Units En Route")
            st.write("Estimated Time of Arrival: 15 mins")
            
            if st.button("Reset System"):
                st.session_state.incident_state = "MONITORING"
                st.rerun()

    # --- Activity Log ---
    with st.expander("📜 Incident Activity Log", expanded=True):
        for log in st.session_state.log_messages:
            if log['type'] == 'error':
                st.error(f"[{log['time']}] {log['msg']}")
            elif log['type'] == 'warning':
                st.warning(f"[{log['time']}] {log['msg']}")
            else:
                st.info(f"[{log['time']}] {log['msg']}")

    # --- Workflow Diagram ---
    with st.expander("How GrazingGuard Works (Human-in-the-Loop Workflow)"):
        st.graphviz_chart("""
        digraph {
            rankdir=TB;
            node [shape=box, style=filled, fillcolor=white];
            
            subgraph cluster_input {
                label = "1. Real-Time Data Collection";
                style=dashed;
                A [label="GPS Tracker on Cattle"];
                B [label="Satellite/Weather Data"];
                C [label="Historical Conflict Data"];
            }

            subgraph cluster_ai {
                label = "2. AI Analysis";
                style=dashed;
                D [label="AI Model\\nIs Risk > 80%?", shape=diamond];
                E [label="Log Data & Continue Monitoring"];
                F [label="TRIGGER RED ALERT", style=filled, fillcolor="#ff4d4d", fontcolor=white];
            }

            subgraph cluster_human {
                label = "3. Human Verification Loop";
                style=dashed;
                G [label="Local Peace Elder", style=filled, fillcolor="#4d94ff", fontcolor=white];
                H [label="Verify with Herder"];
                I [label="Is it a Raid?", shape=diamond];
                J [label="Mark as Safe"];
                K [label="ACTIVATE RESPONSE", style=filled, fillcolor="#ff0000", fontcolor=white];
            }

            subgraph cluster_action {
                label = "4. Security Response";
                style=dashed;
                L [label="Police/Anti-Stock Theft Unit"];
                M [label="Neighboring Communities"];
            }

            A -> D [label="Location/Speed"];
            B -> D [label="Drought Index"];
            C -> D [label="Risk History"];

            D -> E [label="No"];
            D -> F [label="Yes"];

            F -> G [label="SMS/WhatsApp"];
            G -> H [label="Phone Call"];
            H -> I [label="Feedback"];

            I -> J [label="No - False Alarm"];
            J -> D [label="Feedback Loop", style=dotted];
            
            I -> K [label="Yes - Confirmed"];

            K -> L [label="Dispatch"];
            K -> M [label="Notify"];
        }
        """)
