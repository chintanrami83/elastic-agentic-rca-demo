# Quick Start Guide

## Step-by-Step Setup

### 1. Navigate to Project Directory
```bash
cd /path/to/elastic-agentic-rca-demo
```

### 2. Run the Test Setup Script
This will:
- Check Python installation
- Create virtual environment
- Install all dependencies
- Test Elasticsearch connection

```bash
./test_setup.sh
```

### 3. If test_setup.sh succeeds, proceed to create indices
```bash
source venv/bin/activate
python scripts/utilities/setup_elasticsearch.py
```

### 4. Check What You Have
```bash
# List all files
ls -la

# Check if scripts exist
ls -la scripts/utilities/

# Your files should include:
# - test_connectivity.py
# - setup_elasticsearch.py  
# - es_client.py
```

## Troubleshooting

### If you get "requirements.txt not found"
Make sure you're in the correct directory:
```bash
pwd
# Should show: /path/to/elastic-agentic-rca-demo
```

### If you get "Python command not found"
Check your Python installation:
```bash
which python3
python3 --version
```

### If virtual environment fails
Try manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## Manual Step-by-Step (If Script Fails)

```bash
# 1. Go to directory
cd /path/to/elastic-agentic-rca-demo

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate it
source venv/bin/activate

# 4. Upgrade pip
pip install --upgrade pip

# 5. Install dependencies
pip install -r requirements.txt

# 6. Test connection
python scripts/utilities/test_connectivity.py

# 7. Setup Elasticsearch
python scripts/utilities/setup_elasticsearch.py
```

## What You Should See

### After test_connectivity.py:
```
✓ Connected to Elasticsearch 9.3.0
✓ Cluster: acmebank-rca-demo
✓ ML Node Available
✓ ELSER Model Found
```

### After setup_elasticsearch.py:
```
✓ Created 10 indices:
  - incidents-servicenow
  - changes-servicenow
  - problems-servicenow
  - logs-infrastructure
  - logs-application
  - traces-apm-appdynamics
  - comms-teams
  - comms-email
  - docs-knowledge
  - code-repository
```

## Files You Currently Have

```
✓ requirements.txt
✓ .env (with Elastic credentials)
✓ .env.example
✓ .gitignore
✓ setup.sh
✓ test_setup.sh
✓ config/elastic.yaml
✓ config/agents.yaml
✓ config/scenarios.yaml
✓ scripts/utilities/es_client.py
✓ scripts/utilities/test_connectivity.py
✓ scripts/utilities/setup_elasticsearch.py
✓ scripts/README.md
✓ data/README.md
✓ docs/README.md
```

## Next Steps (After Setup Works)

1. I'll create data generation scripts
2. I'll create data ingestion scripts
3. I'll create the 7 agent implementations
4. We'll test end-to-end scenarios

## Need Help?

Contact: Chintan Rami
Demo Date: Feb 11, 2026 @ 2:00 PM AEDT
