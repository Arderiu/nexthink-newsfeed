#!/usr/bin/env bash

echo "Starting Nexthink Challenge..."

# Start API server
echo "Launching FastAPI on 127.0.0.1:8000"
uvicorn app.api:app \
    --host 127.0.0.1 \
    --port 8000 \
    --reload &
API_PID=$!

# Start background fetch loop
echo "Launching background news fetcher..."
python -m scripts.fetch_sources_loop &
FETCH_PID=$!

# Trap CTRL+C
trap "echo 'Shutting down...'; kill $API_PID $FETCH_PID" INT

# Wait so that script doesn't exit
wait
