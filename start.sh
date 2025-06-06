#!/bin/bash

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start API server in background
echo "Starting API server..."
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000 &

# Wait for API server to start
sleep 2

# Start Streamlit app
echo "Starting Streamlit app..."
streamlit run app.py
