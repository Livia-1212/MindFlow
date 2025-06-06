#!/bin/bash

# 1. Create & activate the virtual environment if it doesn’t exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# 2. Install backend dependencies
echo "Installing backend dependencies..."
pip install -r mindflow/backend/requirements.txt

# 3. Install frontend dependencies
echo "Installing frontend dependencies..."
pip install -r mindflow/frontend/requirements.txt

# 4. Start the FastAPI backend in the background
echo "Starting FastAPI backend..."
cd mindflow/backend
uvicorn api:app --reload --host 0.0.0.0 --port 8000 &

# 5. Give the backend a moment to spin up
sleep 2

# 6. Start the Streamlit frontend
echo "Starting Streamlit frontend..."
cd ../frontend
streamlit run app.py
