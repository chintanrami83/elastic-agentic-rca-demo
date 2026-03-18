#!/bin/bash

# Stop Continuous Memory Leak Generator
# Gracefully stops the background generator process

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$SCRIPT_DIR/generator.pid"
LOG_FILE="$SCRIPT_DIR/generator.log"

echo "=========================================="
echo "STOPPING CONTINUOUS DATA GENERATOR"
echo "=========================================="
echo ""

# Check if PID file exists
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  Generator is not running (no PID file found)"
    exit 0
fi

# Read PID
PID=$(cat "$PID_FILE")

# Check if process is actually running
if ! ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Generator process not found (PID: $PID)"
    echo "🧹 Cleaning up PID file..."
    rm "$PID_FILE"
    exit 0
fi

# Send graceful shutdown signal
echo "⏸️  Sending shutdown signal to PID $PID..."
kill -TERM $PID

# Wait for graceful shutdown (max 10 seconds)
echo "⏳ Waiting for graceful shutdown..."
COUNTER=0
while ps -p $PID > /dev/null 2>&1 && [ $COUNTER -lt 10 ]; do
    sleep 1
    COUNTER=$((COUNTER + 1))
    echo -n "."
done
echo ""

# Check if still running
if ps -p $PID > /dev/null 2>&1; then
    echo "⚠️  Process still running after 10 seconds"
    echo "💪 Forcing shutdown..."
    kill -9 $PID
    sleep 1
fi

# Verify stopped
if ps -p $PID > /dev/null 2>&1; then
    echo "❌ Failed to stop generator!"
    exit 1
else
    echo "✅ Generator stopped successfully"
    rm "$PID_FILE"
    echo ""
    echo "📊 Final log output:"
    echo "   tail $LOG_FILE"
    echo ""
    echo "=========================================="
fi
