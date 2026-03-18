# Data Generation & Ingestion Guide

## 🎯 Overview

These scripts generate realistic synthetic data for 3 RCA demo scenarios and load them into Elasticsearch.

## 📦 Files Created

### Data Generation
- `generate_all_scenarios.py` - Master generator (currently Scenario 1 only)

### Data Ingestion  
- `ingest_all_data.py` - Loads all data into Elasticsearch

## 🚀 Quick Start

### Step 1: Generate Data

```bash
cd /path/to/elastic-agentic-rca-demo
source venv/bin/activate
python scripts/data_generation/generate_all_scenarios.py
```

**What it does:**
- Creates synthetic data for Scenario 1 (Connection Pool Exhaustion)
- Generates ~2,500 documents with temporal correlation
- Saves JSON files to `data/synthetic/`

**Expected output:**
```
Generating Scenario 1: Connection Pool Exhaustion
  ✓ Saved 1 documents to scenario1_incidents.json
  ✓ Saved 2 documents to scenario1_changes.json
  ✓ Saved 1200 documents to scenario1_logs_app.json
  ✓ Saved 850 documents to scenario1_logs_infra.json
  ✓ Saved 450 documents to scenario1_traces.json
  ✓ Saved 6 documents to scenario1_teams.json
  ✓ Saved 2 documents to scenario1_emails.json
  ✓ Saved 1 documents to scenario1_kb.json
✓ Scenario 1 complete
```

### Step 2: Ingest Data

```bash
python scripts/data_ingestion/ingest_all_data.py
```

**What it does:**
- Loads all generated JSON files into Elasticsearch
- Uses bulk API for efficiency
- Maps data to correct indices (rca-*)

**Expected output:**
```
✓ Connected to Elasticsearch 9.3.0
✓ Cluster: c7829d8aca4a4b3f80aaa7e474f8f712

Ingesting Scenario 1
  ✓ Indexed 1 documents to rca-incidents
  ✓ Indexed 2 documents to rca-changes
  ✓ Indexed 1200 documents to rca-logs-app
  ✓ Indexed 850 documents to rca-logs-infra
  ✓ Indexed 450 documents to rca-traces
  ✓ Indexed 6 documents to rca-comms-teams
  ✓ Indexed 2 documents to rca-comms-email
  ✓ Indexed 1 documents to rca-knowledge
✓ Scenario 1: 2511 total documents

Document counts by index:
  rca-incidents: 1 documents
  rca-changes: 2 documents
  rca-logs-app: 1,200 documents
  rca-logs-infra: 850 documents
  rca-traces: 450 documents
  rca-comms-teams: 6 documents
  rca-comms-email: 2 documents
  rca-knowledge: 1 documents

Total ingested: 2,511 documents
```

## 📊 Scenario 1 Details

**Incident:** INC0012345  
**Application:** CustomerPortal-API (APP-2847)  
**Timeline:** Feb 8, 2026, 01:45 - 04:15 AEDT (2.5 hours)  
**Issue:** Database connection pool exhaustion after deployment  

### Data Generated

| Type | Count | Description |
|------|-------|-------------|
| Incidents | 1 | Main incident record |
| Changes | 2 | Deployment + emergency fix |
| App Logs | 1,200 | Error logs showing connection failures |
| Infra Logs | 850 | Database server metrics |
| APM Traces | 450 | Slow transactions |
| Teams Messages | 6 | Investigation thread |
| Emails | 2 | Alert notifications |
| KB Articles | 1 | Connection pool tuning guide |

### Temporal Correlation

The data is carefully timestamped to show causality:

1. **01:45** - Deployment (CHG0089234)
2. **02:15** - First connection errors appear
3. **02:30** - Error rate spikes
4. **02:40** - Incident created (INC0012345)
5. **02:42** - Teams investigation starts
6. **03:30** - Root cause identified
7. **03:50** - Emergency fix deployed
8. **04:15** - Incident resolved

## 🔍 Verify in Kibana

Open Kibana: ${KIBANA_URL}

### Check Data

**Discover → Create Data View:**
- Index pattern: `rca-*`
- Time field: `@timestamp` or `created_at`

**Sample Queries:**

```
# All incident data
incident_ref:"INC0012345"

# Error logs
log_level:"ERROR" AND app_id:"APP-2847"

# Slow traces
duration_ms:>5000

# Teams investigation
channel:"incident-customerportal"
```

## 📁 Generated Files Location

```
/path/to/elastic-agentic-rca-demo/data/synthetic/
├── incidents/
│   └── scenario1_incidents.json
├── changes/
│   └── scenario1_changes.json
├── logs/
│   ├── scenario1_logs_app.json
│   └── scenario1_logs_infra.json
├── traces/
│   └── scenario1_traces.json
├── comms/
│   ├── scenario1_teams.json
│   └── scenario1_emails.json
└── knowledge/
    └── scenario1_kb.json
```

## 🔧 Troubleshooting

### "No such file or directory"
Make sure you're in the project root:
```bash
cd /path/to/elastic-agentic-rca-demo
pwd  # Should show the project directory
```

### "Module not found"
Activate virtual environment:
```bash
source venv/bin/activate
```

### "Connection refused"
Check Elasticsearch is accessible:
```bash
python scripts/utilities/test_connectivity.py
```

### No data in Elasticsearch
1. Check data was generated: `ls -lh data/synthetic/logs/`
2. Re-run ingestion: `python scripts/data_ingestion/ingest_all_data.py`
3. Verify in Kibana Discover

## ✅ Success Criteria

After running both scripts, you should have:
- ✓ ~2,500 documents in Elasticsearch
- ✓ Data visible in Kibana Discover
- ✓ Incident INC0012345 searchable
- ✓ Error logs from Feb 8 02:15-04:15
- ✓ Teams messages in timeline

## 🎯 Next Steps

Once data is loaded:
1. Verify in Kibana that data looks correct
2. I'll create Scenarios 2 & 3 (add ~5,000 more documents)
3. I'll build the 7 AI agents to analyze this data
4. We'll create Kibana dashboards
5. Build the demo runner for Feb 11 presentation

## 📝 Notes

- Currently only Scenario 1 is implemented
- Scenarios 2 & 3 will be added in next iteration
- All data uses `rca-*` index prefix to avoid conflicts
- Data is purely synthetic but realistic
- Timestamps are in AEDT (Sydney timezone)
