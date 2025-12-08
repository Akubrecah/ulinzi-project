import streamlit as st
import pandas as pd
import plotly.express as px
import time
import requests
from datetime import datetime, timezone

API_URL = "http://localhost:8000"

# --- SMS CONFIGURATION (TextBee) ---
def send_alert_sms(api_key, device_id, recipients, message):
    try:
        # Ensure recipients is a list
        if isinstance(recipients, str):
            recipients = [recipients]
            
        resp = requests.post(f"{API_URL}/sms/send", json={
            "recipients": recipients,
            "message": message
        }, params={"api_key": api_key, "device_id": device_id})
        
        if resp.status_code == 200:
            return True, resp.json()
        else:
            return False, resp.text
    except Exception as e:
        return False, str(e)

def check_for_sms_reply(api_key, device_id, sender_phone, min_timestamp=None):
    try:
        # sender_phone is list or str, convert to comma string for query param
        if isinstance(sender_phone, list):
            phones = ",".join(sender_phone)
        else:
            phones = sender_phone
            
        params = {
            "api_key": api_key,
            "device_id": device_id,
            "sender_phone": phones
        }
        if min_timestamp:
            params["min_timestamp"] = str(min_timestamp)
            
        resp = requests.get(f"{API_URL}/sms/check", params=params)
        if resp.status_code == 200:
            data = resp.json()
            return data["found"], data["result"], data["debug"]
        else:
            return False, f"API Error: {resp.text}", []
    except Exception as e:
        return False, str(e), []

# --- 1. THE DATA SIMULATOR (Via API) ---
def get_cattle_data(mode="Normal", num_cows=50, center_lat=1.433, center_lon=35.115):
    try:
        resp = requests.post(f"{API_URL}/cattle/data", json={
            "mode": mode,
            "num_cows": num_cows,
            "center_lat": center_lat,
            "center_lon": center_lon
        })
        if resp.status_code == 200:
            return pd.DataFrame(resp.json())
        else:
            st.error(f"Failed to fetch cattle data: {resp.text}")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Connection Error: {e}")
        return pd.DataFrame()

def render_grazing_guard(region_name="West Pokot", region_coords=[1.433, 35.115]):
    # --- 3. STREAMLIT DASHBOARD UI (NSA THEME) ---
    
    # Custom CSS for Tactical/NSA Look
    st.markdown("""
        <style>
            /* Force Dark Background */
            .stApp {
                background-color: #0e1117;
                color: #00ff41; /* Hacker Green */
                font-family: 'Courier New', Courier, monospace;
            }
            
            /* Headings */
            h1, h2, h3 {
                color: #00ff41 !important;
                text-transform: uppercase;
                letter-spacing: 2px;
                border-bottom: 1px solid #00ff41;
                padding-bottom: 10px;
            }
            
            /* Metrics */
            div[data-testid="stMetricValue"] {
                color: #00ff41 !important;
                font-family: 'Courier New', monospace;
                text-shadow: 0 0 5px #00ff41;
            }
            div[data-testid="stMetricLabel"] {
                color: #00cc96 !important;
            }
            
            /* Buttons (Tactical Style) */
            div.stButton > button {
                background-color: #000000;
                color: #00ff41;
                border: 1px solid #00ff41;
                border-radius: 0px;
                font-family: 'Courier New', monospace;
                text-transform: uppercase;
                transition: all 0.3s ease;
            }
            div.stButton > button:hover {
                background-color: #00ff41;
                color: #000000;
                box-shadow: 0 0 10px #00ff41;
            }
            
            /* Alerts/Status Containers */
            div[data-testid="stStatusWidget"] {
                background-color: #000000;
                border: 1px solid #00ff41;
            }
            
            /* Expander */
            .streamlit-expanderHeader {
                background-color: #1c1c1c;
                color: #00ff41 !important;
                border: 1px solid #333;
            }
            
            /* Sidebar */
            section[data-testid="stSidebar"] {
                background-color: #050505;
                border-right: 1px solid #333;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("🛡️ GRAZING GUARD // TACTICAL OPS")
    st.markdown(f"**SYSTEM STATUS:** `ONLINE` | **SECTOR:** `{region_name.upper()}` | **ENCRYPTION:** `AES-256`")
    
    # Initialize Session State for Workflow
    if 'incident_state' not in st.session_state:
        st.session_state.incident_state = "MONITORING" # MONITORING, THREAT_DETECTED, WAITING_FOR_CHIEF, DISPATCHED
    if 'log_messages' not in st.session_state:
        st.session_state.log_messages = []
    if 'alert_sent_time' not in st.session_state:
        st.session_state.alert_sent_time = None

    if 'elder_a_vote' not in st.session_state:
        st.session_state.elder_a_vote = None
    if 'elder_b_vote' not in st.session_state:
        st.session_state.elder_b_vote = None
    if 'third_party_vote' not in st.session_state:
        st.session_state.third_party_vote = None

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
    
    # Updated to Text Area for multiple numbers
    elder_phones_input = st.sidebar.text_area(
        "Elder Phone Numbers (comma separated):", 
        value="+254719299900, +254700000000", 
        help="Enter up to 5 numbers, separated by commas."
    )

    # n8n Webhook URL and Telegram Chat ID
    n8n_webhook_url = st.sidebar.text_input(
        "n8n Webhook URL (Optional):",
        value="https://vmi2955047.contaboserver.net/webhook/863ccad9-ebba-4970-aaa5-c042aeea478c",
        help="Enter your n8n Webhook URL to forward alerts to Telegram."
    )
    
    telegram_chat_id = st.sidebar.text_input(
        "Telegram Chat ID:",
        value="123456789",
        help="Your Telegram chat ID. Get it from @userinfobot on Telegram."
    )
    
    # Alert Method Selection
    alert_method = st.sidebar.radio(
        "Alert Method:",
        ["Both (SMS + Telegram)", "SMS Only", "Telegram Only"],
        help="Choose how to send threat alerts"
    )
    
    # Parse phone numbers
    elder_phones = [p.strip() for p in elder_phones_input.split(",") if p.strip()]
    
    sim_mode = st.sidebar.radio("Herd Activity State:", ["Normal Grazing", "Active Raid Simulation"])

    # Reset state if simulation mode changes to Normal
    if sim_mode == "Normal Grazing" and st.session_state.incident_state != "MONITORING":
        st.session_state.incident_state = "MONITORING"
        st.session_state.log_messages = []
        st.session_state.elder_a_vote = None
        st.session_state.elder_b_vote = None
        st.session_state.third_party_vote = None

    # Generate Live Data based on selection
    # Use the passed region_coords (lat, lon)
    live_data = get_cattle_data(
        "Normal" if sim_mode == "Normal Grazing" else "Raid", 
        center_lat=region_coords[0], 
        center_lon=region_coords[1]
    )
    
    if not live_data.empty:
        # Run AI Prediction via API
        try:
            pred_resp = requests.post(f"{API_URL}/cattle/predict", json=live_data.to_dict(orient="records"))
            if pred_resp.status_code == 200:
                live_data['status'] = pred_resp.json()
            else:
                live_data['status'] = "Safe" # Default fallback
        except:
            live_data['status'] = "Safe"

        # Detect if ANY cow is showing raid identity
        raid_detected = "THREAT DETECTED" in live_data['status'].values
        threat_count = (live_data['status'] == "THREAT DETECTED").sum()
        
        if raid_detected and st.session_state.incident_state == "MONITORING":
            st.session_state.incident_state = "THREAT_DETECTED"
            max_speed = live_data['speed_kmh'].max()
            avg_speed = live_data['speed_kmh'].mean()
            add_log(f"⚠️ THREAT: {threat_count} cows detected at {max_speed:.1f} km/h (avg: {avg_speed:.1f})", "error")
            # Reset votes for new incident
            st.session_state.elder_a_vote = None
            st.session_state.elder_b_vote = None
            st.session_state.third_party_vote = None

        # --- MAIN LAYOUT ---
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader(f"📍 LIVE GEOSPATIAL TRACKING ({region_name.upper()})")
            
            # Using Plotly for the Map
            fig = px.scatter_mapbox(
                live_data, 
                lat="lat", 
                lon="lon", 
                color="status",
                color_discrete_map={"Safe": "#00FF41", "THREAT DETECTED": "#FF0000"}, # Neon Green / Neon Red
                zoom=12, 
                height=500,
                size="speed_kmh", # Faster cows appear larger
                hover_data=["speed_kmh", "id"]
            )
            fig.update_layout(mapbox_style="carto-darkmatter") # Dark Theme
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
                
                if st.button("📲 Send Alert to Chief"):
                    msg = f"ULINZI ALERT: Suspected Raid in {region_name}. Please CONFIRM status immediately."
                    alerts_sent = []
                    
                    # Send SMS if method includes SMS
                    if "SMS" in alert_method or "Both" in alert_method:
                        if elder_phones:
                            with st.spinner(f"Sending SMS to {len(elder_phones)} recipients..."):
                                success, resp = send_alert_sms(TEXTBEE_API_KEY, TEXTBEE_DEVICE_ID, elder_phones, msg)
                                if success:
                                    alerts_sent.append(f"SMS to {len(elder_phones)} recipients")
                                    add_log(f"📱 SMS Alert sent to {len(elder_phones)} recipients.", "warning")
                                else:
                                    st.error(f"SMS Failed: {resp}")
                        else:
                            st.error("Please enter at least one Phone Number for SMS.")
                    
                    # Send Telegram if method includes Telegram
                    if "Telegram" in alert_method or "Both" in alert_method:
                        if n8n_webhook_url and telegram_chat_id:
                            try:
                                n8n_payload = {
                                    "webhook_url": n8n_webhook_url,
                                    "message": msg,
                                    "data": {
                                        "chatId": telegram_chat_id,
                                        "region": region_name,
                                        "timestamp": str(datetime.now()),
                                        "threat_level": "HIGH"
                                    }
                                }
                                resp = requests.post(f"{API_URL}/alerts/n8n", json=n8n_payload)
                                if resp.status_code == 200:
                                    alerts_sent.append("Telegram")
                                    add_log("📱 Telegram Alert Sent.", "info")
                                else:
                                    st.error(f"Telegram Failed: {resp.text}")
                            except Exception as e:
                                st.error(f"Telegram Error: {e}")
                        else:
                            st.warning("Telegram: Please configure Webhook URL and Chat ID.")
                    
                    # If at least one alert was sent successfully, proceed
                    if alerts_sent:
                        st.session_state.incident_state = "WAITING_FOR_CHIEF"
                        st.session_state.alert_sent_time = datetime.now(timezone.utc)
                        st.success(f"✅ Alerts sent via: {', '.join(alerts_sent)}")
                        st.rerun()

            elif st.session_state.incident_state == "WAITING_FOR_CHIEF":
                st.info("⏳ VERIFICATION PROTOCOL INITIATED")
                
                col_a, col_b = st.columns(2)
                
                with col_a:
                    st.markdown("### 👴 Elder A (Community)")
                    if st.session_state.elder_a_vote is None:
                        col_a1, col_a2 = st.columns(2)
                        if col_a1.button("SAFE", key="a_safe"): st.session_state.elder_a_vote = "SAFE"; st.rerun()
                        if col_a2.button("THREAT", key="a_threat"): st.session_state.elder_a_vote = "THREAT"; st.rerun()
                    else:
                        st.write(f"Vote: {st.session_state.elder_a_vote}")
                        
                with col_b:
                    st.markdown("### 🔭 Elder B (Scout)")
                    if st.session_state.elder_b_vote is None:
                        col_b1, col_b2 = st.columns(2)
                        if col_b1.button("SAFE", key="b_safe"): st.session_state.elder_b_vote = "SAFE"; st.rerun()
                        if col_b2.button("THREAT", key="b_threat"): st.session_state.elder_b_vote = "THREAT"; st.rerun()
                    else:
                        st.write(f"Vote: {st.session_state.elder_b_vote}")

                st.markdown("---")

                # --- LOGIC ENGINE ---
                if st.session_state.elder_a_vote and st.session_state.elder_b_vote:
                    
                    # SCENARIO 1: CONSENSUS (Both Agree)
                    if st.session_state.elder_a_vote == st.session_state.elder_b_vote:
                        final_decision = st.session_state.elder_a_vote
                        if final_decision == "SAFE":
                            st.success("✅ CONSENSUS: FALSE ALARM. STANDING DOWN.")
                            if st.button("Reset System"):
                                st.session_state.incident_state = "MONITORING"
                                st.rerun()
                        else:
                            st.error("🚀 CONSENSUS: THREAT CONFIRMED. POLICE DISPATCHED.")
                            st.toast("Police Units Deployed!", icon="🚓")
                            if st.button("Proceed to Dispatch"):
                                st.session_state.incident_state = "DISPATCHED"
                                st.rerun()

                    # SCENARIO 2: CONFLICT (They Disagree) -> THIRD PARTY
                    else:
                        st.warning("⚠️ CONFLICT OF INTEREST DETECTED")
                        st.write("Votes do not match. Escalating to Neutral Third Party.")
                        
                        st.markdown("### ⚖️ Area Chief (Neutral)")
                        col_c1, col_c2 = st.columns(2)
                        if st.session_state.third_party_vote is None:
                            if col_c1.button("RULING: SAFE", key="c_safe"): 
                                st.session_state.third_party_vote = "SAFE"
                                st.rerun()
                            if col_c2.button("RULING: THREAT", key="c_threat"): 
                                st.session_state.third_party_vote = "THREAT"
                                st.rerun()
                        
                        # Final Ruling Display
                        if st.session_state.third_party_vote == "SAFE":
                            st.success("✅ CHIEF RULING: STAND DOWN.")
                            if st.button("Reset System"):
                                st.session_state.incident_state = "MONITORING"
                                st.rerun()
                        elif st.session_state.third_party_vote == "THREAT":
                            st.error("🚀 CHIEF RULING: ACTION AUTHORIZED.")
                            st.toast("Chief Authorized Dispatch!", icon="👮")
                            if st.button("Proceed to Dispatch"):
                                st.session_state.incident_state = "DISPATCHED"
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
    with st.expander("SYSTEM ARCHITECTURE // WORKFLOW"):
        st.graphviz_chart("""
        digraph {
            bgcolor="#0e1117";
            rankdir=TB;
            node [shape=box, style="filled,rounded", fillcolor="#000000", color="#00ff41", fontcolor="#00ff41", fontname="Courier New"];
            edge [color="#00ff41", fontcolor="#00ff41", fontname="Courier New"];
            
            subgraph cluster_input {
                label = "1. DATA INGESTION";
                color="#333";
                fontcolor="#00ff41";
                style=dashed;
                A [label="GPS TRACKER"];
                B [label="SAT DATA"];
                C [label="INTEL DB"];
            }

            subgraph cluster_ai {
                label = "2. THREAT ANALYSIS";
                color="#333";
                fontcolor="#00ff41";
                style=dashed;
                D [label="AI MODEL\\nRISK > 80%?", shape=diamond];
                E [label="LOG & MONITOR"];
                F [label="RED ALERT", fillcolor="#FF0000", fontcolor="black"];
            }

            subgraph cluster_human {
                label = "3. HUMAN VERIFICATION";
                color="#333";
                fontcolor="#00ff41";
                style=dashed;
                G [label="PEACE ELDER", fillcolor="#00ff41", fontcolor="black"];
                H [label="VERIFY"];
                I [label="CONFIRMED?", shape=diamond];
                J [label="FALSE ALARM"];
                K [label="ACTIVATE", fillcolor="#FF0000", fontcolor="black"];
            }

            subgraph cluster_action {
                label = "4. TACTICAL RESPONSE";
                color="#333";
                fontcolor="#00ff41";
                style=dashed;
                L [label="ASTU UNIT"];
                M [label="COMMUNITY"];
            }

            A -> D;
            B -> D;
            C -> D;

            D -> E [label="NO"];
            D -> F [label="YES"];

            F -> G [label="SMS"];
            G -> H;
            H -> I;

            I -> J [label="NO"];
            J -> D [style=dotted];
            
            I -> K [label="YES"];

            K -> L [label="DISPATCH"];
            K -> M [label="NOTIFY"];
        }
        """)
