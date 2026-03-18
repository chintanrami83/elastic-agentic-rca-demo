#!/bin/bash
# Elastic Agentic RCA Demo — Setup Script

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✓${NC} $1"; }
err()  { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
info() { echo -e "${BLUE}ℹ${NC} $1"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Elastic Agentic RCA Demo — Setup     ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Step 1: Check Python
info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
if [ "$PYTHON_MINOR" -ge 11 ]; then
    ok "Python $PYTHON_VERSION"
else
    err "Python 3.11+ required (found $PYTHON_VERSION). See PYTHON313_FIX.md"
    exit 1
fi

# Step 2: Virtual environment
echo ""
info "Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "Virtual environment created"
else
    warn "Virtual environment already exists — skipping"
fi
source venv/bin/activate
ok "Virtual environment activated"

# Step 3: Install dependencies
echo ""
info "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
if pip install -r requirements-minimal.txt > /dev/null 2>&1; then
    ok "Dependencies installed"
else
    err "Dependency install failed — try: pip install -r requirements-minimal.txt"
    exit 1
fi

# Step 4: Configure .env
echo ""
info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    warn ".env created from .env.example"
    echo ""
    echo -e "${YELLOW}  Edit .env and set:${NC}"
    echo "    ELASTIC_URL"
    echo "    ELASTIC_USERNAME"
    echo "    ELASTIC_PASSWORD"
    echo "    KIBANA_URL"
    echo ""
    read -p "  Press Enter after editing .env..."
else
    ok ".env file found"
fi

# Step 5: Test connectivity
echo ""
info "Testing Elasticsearch connectivity..."
if python scripts/utilities/test_connectivity.py; then
    ok "Elasticsearch connection successful"
else
    err "Cannot connect — check your .env credentials"
    exit 1
fi

# Step 6: Create indices
echo ""
read -p "Create Elasticsearch indices? (y/n) " -n 1 -r; echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/utilities/setup_elasticsearch.py
    ok "Indices created"
fi

# Step 7: Ingest data
echo ""
read -p "Ingest demo data (all 3 scenarios)? (y/n) " -n 1 -r; echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python scripts/data_ingestion/ingest_all_data.py
    ok "Data ingested"
fi

# Done
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  Setup complete!                       ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "  1. Open Kibana and create a data view: index pattern rca-*, time field @timestamp"
echo "  2. Verify data: search incident_id:\"INC0012345\" in Discover"
echo "  3. See QUICKSTART.md for running the demo scenarios"
echo ""
