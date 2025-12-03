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
from synthetic_data import generate_time_series_data, generate_live_update
from lstm_model import train_model, predict_next
from grazing_guard import render_grazing_guard

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
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()

# --- Initialization ---
if 'data' not in st.session_state:
    locations = ["Turkana County", "West Pokot County", "Baringo County", "Elgeyo Marakwet"]
    st.session_state.data = generate_time_series_data(locations, days=60)
    st.session_state.locations = locations
    st.session_state.models = {}
    st.session_state.scalers = {}
    
    # Train models initially
    with st.spinner("Initializing AI Models..."):
        for loc in locations:
            model, scaler = train_model(st.session_state.data, loc, epochs=50)
            if model:
                st.session_state.models[loc] = model
                st.session_state.scalers[loc] = scaler

# --- Background Image (Optional - keeping it for style if needed, but map covers main area) ---
# You might want to remove this if it interferes with the map, but let's keep it for the sidebar/header styling
script_dir = os.path.dirname(os.path.abspath(__file__))
# image_path = os.path.join(script_dir, "base_map.png") # Not used for map anymore
# img = get_resized_img_as_base64(image_path)

page_bg_img = f"""
<style>
/* 
[data-testid="stAppViewContainer"] {{
background-image: url("data:image/png;base64,IMG_PLACEHOLDER");
background-size: cover;
background-position: top left;
background-repeat: no-repeat;
background-attachment: local;
}}
*/

[data-testid="stHeader"] {{
background: rgba(0,0,0,0);
}}

[data-testid="stToolbar"] {{
right: 2rem;
}}
</style>
"""
# st.markdown(page_bg_img.replace("IMG_PLACEHOLDER", img), unsafe_allow_html=True) 
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.header("Dashboard Controls")

# Navigation
app_mode = st.sidebar.radio("Navigate to:", ["Regional Dashboard", "GrazingGuard (Cattle Tracking)"])

if app_mode == "GrazingGuard (Cattle Tracking)":
    render_grazing_guard()
    st.stop() # Stop execution of the rest of the script (Regional Dashboard)

selected_location = st.sidebar.selectbox(
    "Choose a location to monitor:",
    st.session_state.locations
)

threat_filter = st.sidebar.slider(
    "Filter by Threat Level:",
    min_value=1,
    max_value=5,
    value=1,
    help="Set the minimum threat level to display."
)

if st.sidebar.button("Simulate Live Update"):
    new_data = generate_live_update(st.session_state.locations)
    st.session_state.data = pd.concat([st.session_state.data, new_data], ignore_index=True)
    st.sidebar.success("Data updated!")

# --- Data Processing for Display ---
latest_data = st.session_state.data.sort_values('Date').groupby('Location').tail(1)
latest_data = latest_data.set_index('Location')

# --- Map Configuration ---
# Coordinates for the counties (approximate centers)
LOCATION_COORDS = {
    "Turkana County": [3.1218, 35.5872],
    "West Pokot County": [1.4942, 35.0472],
    "Baringo County": [0.4667, 35.9667],
    "Elgeyo Marakwet": [1.0498, 35.4782],
}

# Determine map center and zoom
if selected_location in LOCATION_COORDS:
    map_center = LOCATION_COORDS[selected_location]
    zoom_level = 9
else:
    map_center = [1.5, 36.0] # Default Kenya center
    zoom_level = 7

# Create Folium Map
m = folium.Map(location=map_center, zoom_start=zoom_level, tiles="OpenStreetMap")

# Add Esri World Imagery (Satellite)
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Satellite',
    overlay=False,
    control=True
).add_to(m)

# Add Labels (Reference Overlay) - Optional, helps identify places on satellite map
folium.TileLayer(
    tiles='https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}',
    attr='Esri',
    name='Esri Labels',
    overlay=True,
    control=True
).add_to(m)

# Add Markers
for location, coords in LOCATION_COORDS.items():
    if location in latest_data.index:
        current_threat = latest_data.loc[location, 'Threat_Level']
        
        # Filter based on threat level
        if current_threat < threat_filter:
            continue

        # Color coding
        if current_threat >= 4:
            color = "red"
        elif current_threat == 3:
            color = "orange"
        elif current_threat == 2:
            color = "beige" # Folium doesn't have 'yellow' marker, 'beige' is close or use custom icon
        else:
            color = "green"
            
        # Create popup content
        popup_html = f"""
        <b>{location}</b><br>
        Threat Level: {current_threat}<br>
        Incidents: {latest_data.loc[location, 'Incident_Count']}
        """
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(popup_html, max_width=200),
            tooltip=f"{location} (Level {current_threat})",
            icon=folium.Icon(color=color, icon="info-sign")
        ).add_to(m)

# --- Main Dashboard Area ---
st.title("Ulinzi Project AI Dashboard", anchor=False)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Satellite Map")
    st_folium(m, use_container_width=True, height=500)

with col2:
    st.subheader(f"Analysis: {selected_location}")
    
    # Historical Chart
    loc_history = st.session_state.data[st.session_state.data['Location'] == selected_location]
    
    chart = alt.Chart(loc_history).mark_line(point=True).encode(
        x='Date:T',
        y='Threat_Level:Q',
        tooltip=['Date', 'Threat_Level', 'Incident_Count']
    ).properties(
        title=f"Threat Level History",
        height=250
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)

    st.subheader("AI Prediction")
    
    if selected_location in st.session_state.models:
        model = st.session_state.models[selected_location]
        scaler = st.session_state.scalers[selected_location]
        
        # Get last 5 data points
        recent_data = loc_history['Threat_Level'].values[-5:]
        
        if len(recent_data) == 5:
            prediction = predict_next(model, recent_data, scaler)
            
            st.metric(label="Predicted Next Threat Level", value=f"{prediction}/5")
            
            if prediction >= 4:
                st.error("High Threat Predicted! Deploy resources.")
            elif prediction == 3:
                st.warning("Elevated Threat. Monitor closely.")
            else:
                st.success("Low Threat. Routine monitoring.")
        else:
            st.info("Not enough data for prediction yet.")
    else:
        st.warning("Model not trained for this location.")

    st.markdown("---")
    st.write("**Latest Stats:**")
    current_threat = latest_data.loc[selected_location, 'Threat_Level']
    current_incidents = latest_data.loc[selected_location, 'Incident_Count']
    st.write(f"Current Threat: **{current_threat}**")
    st.write(f"Incidents Today: **{current_incidents}**")
