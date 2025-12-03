import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.ensemble import IsolationForest
import time

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
        
        else:
            st.success("System Status: MONITORING")
            st.markdown("No anomalies detected in current grazing patterns.")

    # --- Workflow Diagram ---
    with st.expander("How GrazingGuard Works (Human-in-the-Loop Workflow)"):
        st.markdown("""
        ```mermaid
        graph TD
            subgraph DATA_INPUT [1. Real-Time Data Collection]
                A[GPS Tracker on Cattle] -->|Location/Speed| D[AI Model]
                B[Satellite/Weather Data] -->|Drought Index| D
                C[Historical Conflict Data] -->|Risk History| D
            end

            subgraph AI_PROCESSING [2. AI Analysis]
                D{Is Risk > 80%?}
                D -->|No| E[Log Data & Continue Monitoring]
                D -->|Yes| F[TRIGGER RED ALERT]
            end

            subgraph HUMAN_LOOP [3. Human Verification Loop]
                F -->|SMS/WhatsApp| G[Local Peace Elder]
                G -->|Phone Call| H[Verify with Herder]
                H -->|Feedback| I{Is it a Raid?}
                
                I -->|No - False Alarm| J[Mark as Safe]
                J -->|Feedback Loop| D
                note[False Alarms retrain the AI<br/>to be smarter next time] -.-> D
                
                I -->|Yes - Confirmed| K[ACTIVATE RESPONSE]
            end

            subgraph ACTION [4. Security Response]
                K -->|Dispatch| L[Police/Anti-Stock Theft Unit]
                K -->|Notify| M[Neighboring Communities]
            end

            style F fill:#ff4d4d,stroke:#333,stroke-width:2px,color:white
            style G fill:#4d94ff,stroke:#333,stroke-width:2px,color:white
            style K fill:#ff0000,stroke:#333,stroke-width:4px,color:white
        ```
        """)
