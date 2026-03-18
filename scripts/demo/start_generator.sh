#!/bin/bash

# Start Continuous Memory Leak Generator
# This runs the generator in the background with logging

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATOR_SCRIPT="$SCRIPT_DIR/continuous_memory_leak_generator.py"
PID_FILE="$SCRIPT_DIR/generator.pid"
LOG_FILE="$SCRIPT_DIR/generator.log"

echo "=========================================="
echo "STARTING CONTINUOUS DATA GENERATOR"
echo "=========================================="
echo ""

# Check if already running
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Generator is already running (PID: $PID)"
        echo "   Use ./stop_generator.sh to stop it first"
        exit 1
    else
        echo "🧹 Cleaning up stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/../../venv" ]; then
    echo "🐍 Activating virtual environment..."
    source "$SCRIPT_DIR/../../venv/bin/activate"
fi

# Start generator in background
echo "🚀 Starting generator..."
echo "   Script: $GENERATOR_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""

nohup python "$GENERATOR_SCRIPT" > "$LOG_FILE" 2>&1 &
GENERATOR_PID=$!

# Save PID
echo $GENERATOR_PID > "$PID_FILE"

# Wait a moment to check if it started successfully
sleep 2

if ps -p $GENERATOR_PID > /dev/null 2>&1; then
    echo "✅ Generator started successfully!"
    echo "   PID: $GENERATOR_PID"
    echo ""
    echo "📊 Monitor with:"
    echo "   tail -f $LOG_FILE"
    echo ""
    echo "⏹️  Stop with:"
    echo "   ./stop_generator.sh"
    echo ""
    echo "=========================================="
else
    echo "❌ Generator failed to start!"
    echo "   Check log: $LOG_FILE"
    rm "$PID_FILE"
    exit 1
fi
