import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
import time
import requests
import json

# --- SMS CONFIGURATION ---
# SMS.to API
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL2F1dGg6ODA4MC9hcGkvdjEvdXNlcnMvYXBpL2tleXMvZ2VuZXJhdGUiLCJpYXQiOjE3NjQ3NjA3ODEsIm5iZiI6MTc2NDc2MDc4MSwianRpIjoiTlJjMzR0U1RCM2VXcDN5WiIsInN1YiI6NDkxNjU2LCJwcnYiOiIyM2JkNWM4OTQ5ZjYwMGFkYjM5ZTcwMWM0MDA4NzJkYjdhNTk3NmY3In0.itrDi3f3d9dR7uOpNqE9heJyrSvjLg_xbzKMtMV4Kq0"
URL = "https://api.sms.to/sms/send"

def send_alert_sms(phone_number, message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "to": phone_number,
        "message": message,
        "sender_id": "ULINZI", # Sender ID (might be overwritten by free tier limitations)
        "bypass_optout": True
    }
    
    try:
        response = requests.post(URL, json=payload, headers=headers)
        if response.status_code == 200 or response.status_code == 201:
            return True, response.json()
        else:
            return False, f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

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
    model = train_model()

    # --- 3. STREAMLIT DASHBOARD UI ---
    st.title("🛡️ GrazingGuard - Cattle Tracking")
    
    # Sidebar Controls (Local to this module)
    st.sidebar.markdown("---")
    st.sidebar.subheader("GrazingGuard Simulation")
    
    # SMS Settings
    elder_phone = st.sidebar.text_input("Elder Phone Number:", value="+254719299900", help="Verified number for testing")
    
    sim_mode = st.sidebar.radio("Herd Activity State:", ["Normal Grazing", "Active Raid Simulation"])

    # Generate Live Data based on selection
    live_data = get_cattle_data("Normal" if sim_mode == "Normal Grazing" else "Raid")

    # Run AI Prediction
    # -1 is Anomaly (Raid), 1 is Normal
    features = live_data[['speed_kmh', 'hour_of_day']]
    live_data['anomaly_score'] = model.predict(features)
    live_data['status'] = live_data['anomaly_score'].apply(lambda x: 'Safe' if x == 1 else 'THREAT DETECTED')
    
    # Detect if ANY cow is showing raid identity
    raid_detected = -1 in live_data['anomaly_score'].values

    # --- MAIN LAYOUT ---
    col1, col2 = st.columns([3, 1])

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
            height=600,
            size="speed_kmh", # Faster cows appear larger
            hover_data=["speed_kmh", "id"]
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("📡 Threat Analysis")
        
        # Metrics
        avg_speed = live_data['speed_kmh'].mean()
        st.metric("Avg Herd Speed", f"{avg_speed:.1f} km/h", delta_color="inverse")
        
        current_hour = live_data['hour_of_day'].iloc[0]
        st.metric("Time of Activity", f"{current_hour}:00 hrs")

        st.markdown("---")
        
        # --- THE HUMAN-IN-THE-LOOP LOGIC ---
        
        if raid_detected:
            st.error("🚨 PRE-RAID IDENTITY DETECTED")
            st.markdown("Identity Signature:\n* High Velocity (>12km/h)\n* Anomalous Time (02:00)\n* Vector Movement")
            
            st.markdown("---")

            st.info("🔒 HUMAN VERIFICATION REQUIRED")
            st.write("Alert sent to: Elder Musa (Kacheliba)")
            
            # The Escalation Timer (Visual only for demo)
            with st.spinner("Waiting for Elder response... (Auto-escalation in 4:59)"):
                time.sleep(1) # Tiny pause for effect
            
            # Interaction Buttons
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✅ Verify: SAFE"):
                    st.success("System Stand-Down. False Alarm Logged.")
                    st.balloons() # Fun visual for 'Success'
            with col_b:
                if st.button("⚠️ Verify: RAID"):
                    st.toast("🚀 POLICE DISPATCHED!", icon="🚓")
                    st.markdown("### 🚓 RESPONSE ACTIVATED")
                    st.write("Dispatching ASTU Unit to Sector 4.")
                    st.write("Notifying Neighbors in Sector 5.")
                    
                    # Send SMS
                    if elder_phone:
                        with st.spinner("Sending SMS Alert..."):
                            msg = "ULINZI ALERT: Confirmed Raid in Sector 4. ASTU Dispatched. Please secure livestock."
                            success, resp = send_alert_sms(elder_phone, msg)
                            if success:
                                st.success(f"✅ SMS Alert sent to {elder_phone}")
                                st.json(resp)
                            else:
                                st.error(f"❌ SMS Failed: {resp}")
                    else:
                        st.warning("⚠️ No phone number provided for SMS alert.")
        
        else:
            st.success("System Status: MONITORING")
            st.markdown("No anomalies detected in current grazing patterns.")

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
