#!/bin/bash
echo "Starting Ngrok..."
# Start Ngrok in the background and redirect output to a log file
ngrok http 5000 > /dev/null 2>&1 &
