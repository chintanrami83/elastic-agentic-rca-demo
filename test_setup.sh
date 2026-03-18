#!/bin/bash

# Westpac RCA Demo - Fixed Setup Script for Python 3.13
# Run this to verify everything is ready

echo "=========================================="
echo "Westpac RCA Demo - Setup (Python 3.13)"
echo "=========================================="
echo ""

# Check if in correct directory
if [ ! -f "requirements-minimal.txt" ]; then
    echo "❌ Error: Please run this from $(pwd)"
    echo "   And make sure you downloaded requirements-minimal.txt"
    exit 1
fi

echo "✓ In correct directory"
echo ""

# Check Python version
echo "Checking Python..."
PYTHON_CMD=$(which python3)
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Python 3 not found"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
echo "✓ Using $PYTHON_CMD (version $PYTHON_VERSION)"
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --quiet --upgrade pip setuptools wheel
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
echo "Using requirements-minimal.txt for Python 3.13 compatibility..."
python -m pip install -r requirements-minimal.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Dependency installation failed"
    echo ""
    echo "Try manually:"
    echo "  source venv/bin/activate"
    echo "  pip install python-dotenv pyyaml elasticsearch faker rich"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Test Elasticsearch connectivity
echo "=========================================="
echo "Testing Elasticsearch Connection..."
echo "=========================================="
echo ""

python scripts/utilities/test_connectivity.py

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Next step:"
    echo "  source venv/bin/activate"
    echo "  python scripts/utilities/setup_elasticsearch.py"
else
    echo ""
    echo "⚠️  Connection test failed - but setup is complete"
    echo ""
    echo "Check your .env file has correct credentials:"
    echo "  cat .env | grep ELASTIC"
    echo ""
    echo "Then try again:"
    echo "  source venv/bin/activate"
    echo "  python scripts/utilities/test_connectivity.py"
fi

echo ""
