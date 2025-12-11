# Split Deployment Guide: Render & Streamlit Cloud

This guide explains how to deploy the **Backend** to Render and the **Frontend** to Streamlit Community Cloud.

## Part 1: Deploy Backend to Render

1.  **Push your latest code** to GitHub.
2.  **Log in to Render** (dashboard.render.com).
3.  Click **New +** -> **Web Service**.
4.  Connect your GitHub repository (`ulinzi-project`).
5.  Render will automatically detect `render.yaml`.
    -   It should show a service named `ulinzi-backend`.
    -   Runtime: Python 3
    -   Build Command: `pip install -r requirements.txt`
    -   Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
6.  Click **Create Web Service**.
7.  **Wait for deployment**. Once live, Render will provide a URL (e.g., `https://ulinzi-backend.onrender.com`).
    -   **COPY THIS URL**. You will need it for the frontend.

## Part 2: Deploy Frontend to Streamlit Cloud

1.  **Log in to Streamlit Cloud** (share.streamlit.io).
2.  Click **New app**.
3.  Select your GitHub repository, branch, and **Main file path**.
    -   **Main file path**: `frontend/app.py`
4.  **Advanced Settings** (Click the `Advanced settings` link):
    -   Go to the **Secrets** or **Environment variables** section (Streamlit Cloud interface varies, look for "Environment variables").
    -   Add a new variable:
        -   **Key**: `API_URL`
        -   **Value**: Your Render Backend URL (e.g., `https://ulinzi-backend.onrender.com`) - *Important: Do NOT add a trailing slash `/`*
5.  Click **Deploy!**.

## Part 3: Verification

1.  Open your deployed Streamlit App.
2.  Try to **Login** (User: `admin`, Pass: `niruhack123`).
    -   If it works, the frontend successfully communicated with the backend!
3.  Check the **Regional Dashboard** to ensure data loads.

## Troubleshooting

-   **Backend 502/Timeout**: Render free tier spins down after inactivity. The first request might take 50+ seconds. Streamlit might time out. Just refresh the Streamlit page.
-   **Connection Error (127.0.0.1)**: This means your Frontend doesn't know where the Backend is.
    -   **Fix**: Go to Streamlit Cloud Settings -> Environment Variables.
    -   Add `API_URL` = `https://ulinzi-project.onrender.com` (Your Render URL).
    -   **Important**: Log out of the app and log back in to verify.
-   **Connection Error**: Check if `API_URL` in Streamlit settings matches the Render URL exactly (https, no trailing slash).

## ⚡ Keeping Your App Awake (Always Online)

Free hosting tiers (Render & Streamlit) go to "sleep" after 15 minutes of inactivity. To keep them running 24/7:

1.  **Use a Free Uptime Monitor**:
    -   Sign up for **UptimeRobot** (uptimerobot.com) or **Cron-job.org**.
2.  **Create 2 Monitors**:
    -   **Monitor 1 (Backend)**: Create a new HTTP(s) monitor for your Render URL (`https://ulinzi-project.onrender.com`). Set interval to **5 minutes**.
    -   **Monitor 2 (Frontend)**: Create a new HTTP(s) monitor for your Streamlit URL (`https://<your-app>.streamlit.app`). Set interval to **10 minutes**.
3.  **Why?**: This sends a "ping" to your servers regularly, tricking them into thinking they are active, so they never spin down.
