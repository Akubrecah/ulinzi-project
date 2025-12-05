import streamlit as st
import base64
from PIL import Image
import io
import os
import pandas as pd
import numpy as np
import altair as alt
import folium
from streamlit_folium import st_folium
import requests
from grazing_guard import render_grazing_guard
from datetime import datetime, timedelta
import extra_streamlit_components as stx
import time

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Ulinzi Project")

# --- Helper Functions ---
@st.cache_data
def get_resized_img_as_base64(file, max_width=1920):
    with Image.open(file) as img:
        width, height = img.size
        if width > max_width:
            new_width = max_width
            new_height = int(new_width * height / width)
            img = img.resize((new_width, new_height))
        
        buffered = io.BytesIO()
API_URL = "http://localhost:8000"

# --- Authentication with Persistence ---
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()

# Wait for the cookie manager to load the cookies
if 'cookie_manager_init' not in st.session_state:
    st.session_state.cookie_manager_init = True
    time.sleep(0.5)

auth_cookie = cookie_manager.get(cookie="ulinzi_auth")

if 'logged_in' not in st.session_state:
    if auth_cookie == "true":
        st.session_state.logged_in = True
    else:
        st.session_state.logged_in = False

def login():
    st.markdown("""
        <style>
            .stTextInput > div > div > input {
                color: #00ff41;
                background-color: #000000;
                border: 1px solid #00ff41;
            }
            .stButton > button {
                width: 100%;
            }
        </style>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔒 RESTRICTED ACCESS")
        st.markdown("### ULINZI COMMAND CENTER")
        
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("AUTHENTICATE"):
            try:
                resp = requests.post(f"{API_URL}/auth/login", json={"username": username, "password": password})
                if resp.status_code == 200:
                    st.session_state.logged_in = True
                    cookie_manager.set("ulinzi_auth", "true", expires_at=datetime.now() + timedelta(days=7))
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Invalid Credentials")
            except Exception as e:
                st.error(f"Connection Error: {e}")

if not st.session_state.logged_in:
    login()
    st.stop()

# --- CUSTOM CSS (NSA THEME) ---
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
        
        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #333;
        }
        
        /* Radio Buttons */
        div[role="radiogroup"] label {
            color: #00ff41 !important;
            font-family: 'Courier New', monospace;
        }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.header("Dashboard Controls")

if st.sidebar.button("LOGOUT"):
    st.session_state.logged_in = False
    cookie_manager.delete("ulinzi_auth")
    st.rerun()

# Global Location Selector (Available for both modes)
locations = {
    "West Pokot": [1.433, 35.115],
    "Turkana": [3.116, 35.600],
    "Baringo": [0.669, 35.953],
    "Samburu": [1.204, 36.926]
}
selected_location = st.sidebar.selectbox("Select Region:", list(locations.keys()))
# --- Navigation ---
page = st.sidebar.radio("Module:", ["Regional Dashboard", "GrazingGuard"])

if page == "GrazingGuard":
    render_grazing_guard(selected_location, locations[selected_location])

elif page == "Regional Dashboard":
    st.title(f"🌍 REGIONAL DASHBOARD: {selected_location.upper()}")
    
    # --- 1. Map Visualization ---
    st.subheader("Geospatial Overview")
    
    # Create Folium Map
    m = folium.Map(location=locations[selected_location], zoom_start=9, tiles="CartoDB dark_matter")
    
    # Add Marker
    folium.Marker(
        locations[selected_location], 
        popup=f"{selected_location} HQ", 
        tooltip="Regional Command",
        icon=folium.Icon(color="green", icon="info-sign")
    ).add_to(m)
    
    # Render Map
    st_folium(m, width=1200, height=400)
    
    # --- 2. Historical Data & Predictions ---
    st.subheader("Historical Trends & Forecast")
    
    # Fetch Data from API
    try:
        resp = requests.get(f"{API_URL}/history/data", params={"locations": selected_location, "days": 60})
        if resp.status_code == 200:
            hist_data = pd.DataFrame(resp.json())
            hist_data['Date'] = pd.to_datetime(hist_data['Date'])
            
            # Train Model Button
            if st.button("Train Prediction Model"):
                with st.spinner("Training LSTM Model..."):
                    # Convert Date back to string for JSON serialization
                    train_data = hist_data.copy()
                    train_data['Date'] = train_data['Date'].dt.strftime('%Y-%m-%d')
                    train_resp = requests.post(f"{API_URL}/history/train", json=train_data.to_dict(orient="records"), params={"location": selected_location})
                    if train_resp.status_code == 200 and train_resp.json().get("status") == "trained":
                        st.success("Model Trained Successfully")
                    else:
                        st.error("Training Failed")

            # Timeframe Selector
            timeframe = st.selectbox("Select Timeframe:", ["Daily", "Weekly", "Monthly", "Quarterly"])
            
            # Resample Data based on Timeframe
            chart_data = hist_data.copy()
            chart_data.set_index('Date', inplace=True)
            
            if timeframe == "Weekly":
                chart_data = chart_data.resample('W').agg({'Incident_Count': 'sum', 'Threat_Level': 'mean'}).reset_index()
            elif timeframe == "Monthly":
                chart_data = chart_data.resample('M').agg({'Incident_Count': 'sum', 'Threat_Level': 'mean'}).reset_index()
            elif timeframe == "Quarterly":
                chart_data = chart_data.resample('Q').agg({'Incident_Count': 'sum', 'Threat_Level': 'mean'}).reset_index()
            else:
                chart_data = chart_data.reset_index()

            # Chart
            chart = alt.Chart(chart_data).mark_line(point=True).encode(
                x=alt.X('Date:T', title='Date'),
                y=alt.Y('Incident_Count:Q', title='Incident Count'),
                tooltip=['Date:T', 'Incident_Count:Q', 'Threat_Level:Q']
            ).properties(
                title=f"{timeframe} Incident Trends in {selected_location}",
                height=300
            ).configure_mark(
                color='#00ff41'
            ).configure_axis(
                labelColor='#00ff41',
                titleColor='#00ff41',
                gridColor='#333'
            ).configure_title(
                color='#00ff41'
            ).configure_view(
                stroke='#333'
            )
            
            st.altair_chart(chart, use_container_width=True)
            
            # Predict Next Week (Always uses Daily Data for accuracy)
            st.subheader("AI Risk Forecast")
            if st.button("Forecast Next 7 Days Risk"):
                # Get last 10 days of raw daily data
                recent_data = hist_data['Incident_Count'].values[-10:].tolist()
                try:
                    pred_resp = requests.post(f"{API_URL}/history/predict", json=recent_data, params={"location": selected_location})
                    if pred_resp.status_code == 200:
                        prediction = pred_resp.json().get("prediction")
                        current_val = hist_data['Incident_Count'].iloc[-1]
                        delta = prediction - current_val
                        
                        st.metric(
                            "Predicted Daily Incidents (Next 7 Days Avg)", 
                            f"{prediction:.1f}", 
                            delta=f"{delta:.1f}",
                            delta_color="inverse"
                        )
                    else:
                        st.warning("Model not trained yet. Please train the model first.")
                except Exception as e:
                    st.error(f"Prediction Error: {e}")
        else:
            st.error("Failed to load history data")
    except Exception as e:
        st.error(f"API Connection Error: {e}")
