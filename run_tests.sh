#!/bin/bash

# Start Flask server in background
cd /Users/seehorn/Downloads/Development/ScholarSidekick
echo "Starting Flask server..."
/Users/seehorn/Downloads/Development/ScholarSidekick/.venv/bin/python run.py > server.log 2>&1 &
SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
echo "Waiting for server to start..."
sleep 5

# Run tests
echo "Running tests..."
/Users/seehorn/Downloads/Development/ScholarSidekick/.venv/bin/python test_api.py

# Kill server
echo "Stopping server..."
kill $SERVER_PID

echo "Done!"
