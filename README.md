# Ulinzi Project - AI-Powered Threat Monitoring Dashboard

## Overview

The **Ulinzi Project** is a cutting-edge monitoring dashboard designed to visualize and predict security threat levels across various counties in Kenya (Turkana, West Pokot, Baringo, Elgeyo Marakwet). It leverages Artificial Intelligence (LSTM networks) to analyze historical data and forecast future threat trends, aiding in proactive resource deployment and decision-making.

## Key Features

-   **Interactive Satellite Map:**
    -   Real-time visualization of monitored locations using high-resolution Esri World Imagery.
    -   Dynamic markers color-coded by threat level (Green, Yellow, Orange, Red).
    -   Interactive popups displaying detailed stats (Threat Level, Incident Count).
-   **AI-Driven Predictions:**
    -   Integrated **Long Short-Term Memory (LSTM)** neural networks powered by PyTorch.
    -   Predicts the next day's threat level based on historical trends.
    -   Provides actionable alerts (e.g., "High Threat Predicted! Deploy resources.").
-   **Synthetic Data Engine:**
    -   Generates realistic time-series data with seasonality and random noise to simulate real-world scenarios.
    -   "Simulate Live Update" feature to mimic real-time data ingestion.
-   **Data Visualization:**
    -   Interactive historical charts using Altair.
    -   Filterable views based on threat severity.

## Tech Stack

-   **Frontend:** [Streamlit](https://streamlit.io/)
-   **Mapping:** [Folium](https://python-visualization.github.io/folium/), [Streamlit-Folium](https://folium.streamlit.app/)
-   **AI/ML:** [PyTorch](https://pytorch.org/), [NumPy](https://numpy.org/)
-   **Data Processing:** [Pandas](https://pandas.pydata.org/)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd ulinzi-project
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

2.  **Navigate the Dashboard:**
    -   **Sidebar:** Select a county to monitor and filter by threat level.
    -   **Live Map:** Explore the satellite view. Markers indicate current status.
    -   **Analysis Panel:** View historical trends and AI predictions for the selected location.
    -   **Simulation:** Click "Simulate Live Update" in the sidebar to generate new data points and see the model update.

## Project Structure

-   `app.py`: Main Streamlit application entry point. Handles UI, map rendering, and interaction.
-   `lstm_model.py`: PyTorch LSTM model definition and training logic.
-   `synthetic_data.py`: Generates realistic synthetic data for demonstration.
-   `test_model.py`: Script to verify the AI model pipeline independently.
-   `requirements.txt`: List of Python dependencies.

## Future Improvements

-   **Real Data Integration:** Connect to a live database (SQL/NoSQL) for real-time incident reporting.
-   **Advanced Models:** Implement more complex architectures (Transformer, GRU) for longer-term forecasting.
-   **User Authentication:** Add login/role-based access for secure deployment.
-   **Alert System:** Integrate SMS/Email notifications for high-threat predictions.

---
*Built for the NIRU HACKATHON 2025*
