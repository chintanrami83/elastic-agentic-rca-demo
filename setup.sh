#!/bin/bash

# Elastic Agentic RCA Demo - Quick Setup Script
# This script sets up the entire demo environment

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root
PROJECT_ROOT="$(pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Elastic Agentic RCA Demo - Quick Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running from correct directory
if [ ! -d "$PROJECT_ROOT" ]; then
    print_error "Project directory not found: $PROJECT_ROOT"
    exit 1
fi

cd "$PROJECT_ROOT"

# Step 1: Check Python version
echo ""
print_info "Step 1: Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
    print_status "Python $PYTHON_VERSION detected"
else
    print_error "Python 3.11+ required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Step 2: Create virtual environment
echo ""
print_info "Step 2: Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 3: Activate virtual environment
source venv/bin/activate
print_status "Virtual environment activated"

# Step 4: Upgrade pip
echo ""
print_info "Step 3: Upgrading pip..."
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
print_status "pip upgraded"

# Step 5: Install dependencies
echo ""
print_info "Step 4: Installing Python dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    print_status "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Step 6: Check for .env file
echo ""
print_info "Step 5: Checking environment configuration..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_warning ".env file created from .env.example"
        print_warning "⚠️  IMPORTANT: Edit .env file with your Elasticsearch credentials"
        echo ""
        echo -e "${YELLOW}Required configuration:${NC}"
        echo "  - ELASTIC_URL"
        echo "  - ELASTIC_USERNAME"
        echo "  - ELASTIC_PASSWORD"
        echo ""
        read -p "Press Enter to continue after editing .env file..."
    else
        print_error ".env.example not found"
        exit 1
    fi
else
    print_status ".env file exists"
fi

# Step 7: Test Elasticsearch connectivity
echo ""
print_info "Step 6: Testing Elasticsearch connectivity..."

# Create a simple connectivity test
cat > /tmp/test_es_connection.py << 'EOF'
import os
import sys
from dotenv import load_dotenv
from elasticsearch import Elasticsearch

load_dotenv()

try:
    es = Elasticsearch(
        os.getenv('ELASTIC_URL'),
        basic_auth=(os.getenv('ELASTIC_USERNAME'), os.getenv('ELASTIC_PASSWORD')),
        verify_certs=False,
        request_timeout=10
    )
    info = es.info()
    print(f"✓ Connected to Elasticsearch {info['version']['number']}")
    sys.exit(0)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    sys.exit(1)
EOF

if python /tmp/test_es_connection.py; then
    print_status "Elasticsearch connection successful"
else
    print_error "Cannot connect to Elasticsearch"
    print_warning "Please check your .env configuration"
    exit 1
fi

# Step 8: Setup Elasticsearch indices
echo ""
print_info "Step 7: Setting up Elasticsearch indices..."
read -p "Do you want to create Elasticsearch indices? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/utilities/setup_elasticsearch.py" ]; then
        python scripts/utilities/setup_elasticsearch.py
        print_status "Elasticsearch indices created"
    else
        print_warning "setup_elasticsearch.py not found yet - will create later"
    fi
else
    print_warning "Skipping Elasticsearch setup"
fi

# Step 9: Generate synthetic data
echo ""
print_info "Step 8: Generating synthetic data..."
read -p "Do you want to generate demo data now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/data_generation/generate_all_scenarios.py" ]; then
        python scripts/data_generation/generate_all_scenarios.py
        print_status "Synthetic data generated"
    else
        print_warning "Data generation scripts not created yet"
    fi
else
    print_warning "Skipping data generation"
fi

# Step 10: Ingest data
echo ""
print_info "Step 9: Ingesting data into Elasticsearch..."
read -p "Do you want to ingest data now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "scripts/data_ingestion/ingest_all_data.py" ]; then
        python scripts/data_ingestion/ingest_all_data.py
        print_status "Data ingested successfully"
    else
        print_warning "Data ingestion scripts not created yet"
    fi
else
    print_warning "Skipping data ingestion"
fi

# Step 11: Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Review and update .env file if needed"
echo "  2. Run: python scripts/data_generation/generate_all_scenarios.py"
echo "  3. Run: python scripts/data_ingestion/ingest_all_data.py"
echo "  4. Run: python agents/orchestrator/main.py --incident INC0012345"
echo ""
echo -e "${BLUE}Quick commands:${NC}"
echo "  Activate venv:  source venv/bin/activate"
echo "  Run tests:      pytest tests/"
echo "  View logs:      tail -f logs/rca-demo.log"
echo "  Open Kibana:    \$KIBANA_URL (from .env)"
echo ""
echo -e "${BLUE}Documentation:${NC}"
echo "  Main README:    cat README.md"
echo "  Data README:    cat data/README.md"
echo "  Scripts README: cat scripts/README.md"
echo ""
print_status "Setup script completed successfully!"
echo ""
