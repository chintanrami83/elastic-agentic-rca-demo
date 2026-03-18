# Westpac RCA Demo - Setup Instructions

## IMPORTANT: Download All Files First!

I've created all the project files, but they need to be downloaded to your Mac.

### Step 1: Download All Files

Download all the files I'm providing below and save them to:
`/path/to/elastic-agentic-rca-demo/`

### Step 2: Create Directory Structure

In Terminal, run:

```bash
cd /path/to/elastic-agentic-rca-demo

# Create directories
mkdir -p config scripts/utilities scripts/data_generation scripts/data_ingestion
mkdir -p data/synthetic/{incidents,changes,problems,logs,traces,comms,knowledge,code}
mkdir -p data/{raw,processed}
mkdir -p agents/{orchestrator,tickets_changes,comms,observability,correlation_rca,pir_generator,reporting}
mkdir -p elastic kibana docs tests logs outputs/{pir_documents,reports} notebooks

# Create __init__.py files
touch scripts/__init__.py scripts/utilities/__init__.py
touch scripts/data_generation/__init__.py scripts/data_ingestion/__init__.py
touch agents/__init__.py
```

### Step 3: Place Downloaded Files

Put the downloaded files in these locations:

```
/path/to/elastic-agentic-rca-demo/
├── requirements.txt          (download this)
├── .env                      (download this)
├── .gitignore                (download this)
├── setup.sh                  (download this)  
├── test_setup.sh             (download this)
├── QUICKSTART.md             (download this)
├── config/
│   ├── elastic.yaml          (download this)
│   ├── agents.yaml           (download this)
│   └── scenarios.yaml        (download this)
└── scripts/utilities/
    ├── __init__.py
    ├── es_client.py          (download this)
    ├── test_connectivity.py  (download this)
    └── setup_elasticsearch.py (download this)
```

### Step 4: Make Scripts Executable

```bash
cd /path/to/elastic-agentic-rca-demo
chmod +x setup.sh test_setup.sh
chmod +x scripts/utilities/*.py
```

### Step 5: Run Setup

```bash
./test_setup.sh
```

This will:
- Create virtual environment
- Install dependencies
- Test Elasticsearch connection

### Step 6: Create Indices

```bash
source venv/bin/activate
python scripts/utilities/setup_elasticsearch.py
```

## Files You Need to Download

I'll provide these files for download:

### Core Files (6 files)
1. requirements.txt
2. .env
3. .gitignore  
4. setup.sh
5. test_setup.sh
6. QUICKSTART.md

### Config Files (3 files)
7. config/elastic.yaml
8. config/agents.yaml
9. config/scenarios.yaml

### Python Scripts (3 files)
10. scripts/utilities/es_client.py
11. scripts/utilities/test_connectivity.py
12. scripts/utilities/setup_elasticsearch.py

## After Setup Works

Once you can successfully run test_connectivity.py and setup_elasticsearch.py, I'll create:
- Data generation scripts
- Data ingestion scripts
- All 7 AI agents
- Kibana dashboards
- Demo runner

## Troubleshooting

If files don't download properly, let me know and I'll provide them in a different format.
