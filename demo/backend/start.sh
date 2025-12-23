#!/bin/bash
# Production startup script for deployment platforms (Render, Railway, etc.)
# This script uses environment variables for configuration

set -e  # Exit on error

echo "🚀 Starting Vietnam Housing Price Prediction API (Production Mode)"
echo "=================================================="

# Check Python version
echo "✓ Python version: $(python3 --version)"

# Check if models directory exists
if [ ! -d "models" ]; then
    echo "⚠️  WARNING: models/ directory not found!"
    echo "   The API will start but predictions may fail."
fi

# Check required environment variables
if [ -z "$PORT" ]; then
    echo "⚠️  PORT not set, using default 8000"
    export PORT=8000
fi

echo "✓ Port: $PORT"
echo "✓ Debug mode: ${DEBUG:-False}"
echo "✓ Log level: ${LOG_LEVEL:-INFO}"

# Display available models
if [ -d "models" ]; then
    MODEL_COUNT=$(ls -1 models/*.pkl 2>/dev/null | wc -l | tr -d ' ')
    echo "✓ Found $MODEL_COUNT model file(s)"
fi

echo "=================================================="
echo "Starting uvicorn server..."
echo ""

# Start the application
# Use exec to replace shell process with uvicorn (for proper signal handling)
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers 1 \
    --log-level "${LOG_LEVEL:-info}" \
    --no-access-log
