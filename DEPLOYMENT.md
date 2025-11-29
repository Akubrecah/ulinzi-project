# Deployment Guide - Hugging Face Spaces

Since Streamlit Cloud is giving errors, the best free alternative for this project (which uses Python and PyTorch) is **Hugging Face Spaces**.

GitHub Pages and Vercel are primarily for static websites and cannot easily run the Python backend required for PyTorch and Streamlit.

## Deploying to Hugging Face Spaces

1.  **Create an Account:**
    -   Go to [huggingface.co](https://huggingface.co/) and sign up for a free account.

2.  **Create a New Space:**
    -   Click on your profile picture -> **New Space**.
    -   **Space Name:** `ulinzi-project` (or similar).
    -   **License:** `MIT` (optional).
    -   **Select the Space SDK:** Choose **Streamlit**.
    -   **Hardware:** Keep it as **CPU Basic (Free)**.
    -   **Privacy:** Public.
    -   Click **Create Space**.

3.  **Upload Files:**
    -   You will be redirected to your new Space.
    -   You can upload files directly via the browser or use Git.
    -   **Files to upload:**
        -   `app.py`
        -   `lstm_model.py`
        -   `synthetic_data.py`
        -   `requirements.txt`
        -   `base_map.png` (if you are still using it, otherwise optional)
        -   `packages.txt` (I will create this for you, it helps with system dependencies)

4.  **Configuration:**
    -   Hugging Face will automatically detect `requirements.txt` and install the libraries.
    -   It will run `app.py` automatically.

## Option 2: Push via Git (Recommended for syncing)

If you have already created the Space on Hugging Face, you can push your code directly from your terminal.

1.  **Add Hugging Face as a Remote:**
    Replace `YOUR_USERNAME` and `SPACE_NAME` with your actual Hugging Face details.
    ```bash
    git remote add space https://huggingface.co/spaces/YOUR_USERNAME/SPACE_NAME
    ```

2.  **Push to Hugging Face:**
    ```bash
    git push --force space main
    ```
    *Note: When asked for your password, you MUST use a **Hugging Face Access Token**, not your account password.*

    **How to get an Access Token:**
    1.  Go to your [Hugging Face Settings > Access Tokens](https://huggingface.co/settings/tokens).
    2.  Click **Create new token**.
    3.  Select **Write** permissions.
    4.  Copy the token (starts with `hf_...`).
    5.  Paste this token when the terminal asks for your password.

## Troubleshooting

If you see errors in the "Logs" tab of your Space:

-   **Memory Issues:** If the app crashes with "OOM" (Out of Memory), it might be because PyTorch is too heavy. We are already using the CPU version in `requirements.txt` which helps.
-   **Missing Dependencies:** Check the logs to see if a specific module is missing.

## Why not GitHub Pages?
GitHub Pages only hosts static files (HTML/CSS/JS). It cannot execute Python code. Since your app needs to run a Neural Network (LSTM) in Python, it requires a server environment like Hugging Face Spaces or Streamlit Cloud.
