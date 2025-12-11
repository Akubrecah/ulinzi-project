#!/bin/bash
echo "Starting Backend..."
# Start Backend in background
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

echo "Starting Frontend..."
# Start Frontend in foreground
python -m streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0
