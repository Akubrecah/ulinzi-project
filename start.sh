#!/bin/bash
# Activate venv
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "Starting Backend..."
# Start Backend in background
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

sleep 3

echo "Starting Frontend..."
# Ensure PORT is set, default to 8501 for local dev
PORT=${PORT:-8501}
# Force API_URL to localhost for local run
export API_URL="http://127.0.0.1:8000"

# Start Frontend
python -m streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0

# When Streamlit exits, kill the backend
kill $BACKEND_PID
