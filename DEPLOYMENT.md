# Deployment Guide - Streamlit Cloud

The best and easiest way to deploy this application is **Streamlit Cloud**. It is free and designed specifically for Streamlit apps.

**Note:** We have fixed the issues that caused the "black screen" earlier (switched to CPU-only PyTorch and fixed map rendering).

## Steps to Deploy

1.  **Push to GitHub:**
    You need to push your code to a public GitHub repository first.
    
    ```bash
    # 1. Create a new repository on GitHub (e.g., 'ulinzi-project')
    
    # 2. Link your local folder to GitHub
    git remote add origin https://github.com/YOUR_USERNAME/ulinzi-project.git
    
    # 3. Push your code
    git push -u --force origin main
    ```

2.  **Deploy on Streamlit Cloud:**
    -   Go to [share.streamlit.io](https://share.streamlit.io/).
    -   Sign in with GitHub.
    -   Click **New app**.
    -   Select your repository (`ulinzi-project`).
    -   Select the branch (`main`).
    -   Select the main file path (`app.py`).
    -   Click **Deploy!**.

## Option 2: Render (Alternative)

If you prefer another provider, **Render** is a great free alternative.

1.  **Push to GitHub:** (Same as above)
    ```bash
    git push -u --force origin main
    ```

2.  **Deploy on Render:**
    -   Go to [render.com](https://render.com/) and sign up.
    -   Click **New +** -> **Web Service**.
    -   Connect your GitHub account and select the `ulinzi-project` repository.
    -   **Name:** `ulinzi-project`
    -   **Runtime:** `Python 3`
    -   **Build Command:** `pip install -r requirements.txt`
    -   **Start Command:** `bash start.sh`
    -   **Note:** We have added a `render.yaml` file to the repository. Render should automatically detect this and configure the service for you if you select "Blueprint" instead of "Web Service", or it will pre-fill these settings.
    -   **Free Tier:** Select "Free".
    -   Click **Create Web Service**.

## System Dependencies
Streamlit Cloud will automatically detect `packages.txt` and install the necessary system libraries (like `libgl1`) required for image processing.

## Python Dependencies
It will also automatically install everything in `requirements.txt`. We have optimized this file to use the CPU version of PyTorch, which is much smaller and faster to install on the cloud.
