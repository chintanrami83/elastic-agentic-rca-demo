# Quick Start Guide

Get the demo running in 15 minutes.

---

## Prerequisites

- Python 3.11 or 3.12 (see [PYTHON313_FIX.md](PYTHON313_FIX.md) for 3.13)
- Elastic Cloud deployment v9.2+ with ELSER model deployed
- Git

---

## Step 1 — Clone and Configure

```bash
git clone https://github.com/your-org/elastic-agentic-rca-demo.git
cd elastic-agentic-rca-demo
cp .env.example .env
```

Edit `.env` with your Elastic Cloud credentials:

```
ELASTIC_URL=https://your-cluster.es.your-region.gcp.elastic-cloud.com
ELASTIC_USERNAME=elastic
ELASTIC_PASSWORD=your-password
KIBANA_URL=https://your-cluster.kb.your-region.gcp.elastic-cloud.com
```

---

## Step 2 — Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

---

## Step 3 — Test Connectivity

```bash
python scripts/utilities/test_connectivity.py
```

Expected:
```
✓ Connected to Elasticsearch 9.x.x
✓ ELSER model found
```

---

## Step 4 — Create Elasticsearch Indices

```bash
python scripts/utilities/setup_elasticsearch.py
```

This creates all `rca-*` indices:
```
✓ rca-incidents
✓ rca-changes
✓ rca-alerts
✓ rca-logs-app
✓ rca-logs-infra
✓ rca-metrics
✓ rca-traces
✓ rca-comms-teams
✓ rca-comms-email
✓ rca-knowledge
```

---

## Step 5 — Ingest Demo Data

```bash
python scripts/data_ingestion/ingest_all_data.py
```

Expected:
```
✓ Scenario 1: 156 documents
✓ Scenario 2: 180 documents
✓ Scenario 3: 228 documents
Total ingested: 564 documents
```

---

## Step 6 — Verify in Kibana

1. Open Kibana → **Discover**
2. Create a data view:
   - Index pattern: `rca-*`
   - Time field: `@timestamp`
3. Run these searches to confirm each scenario loaded:

| Search | Expected docs |
|---|---|
| `incident_id:"INC0012345"` | ~156 (Scenario 1) |
| `incident_id:"INC0023456"` | ~180 (Scenario 2) |
| `incident_id:"INC0034567"` | ~228 (Scenario 3) |

---

## Step 7 — Run the Demo

### Scenario 1 — Manual RCA
In Kibana, open the Elastic Workflow for manual RCA and enter:
```
incident_id: INC0012345
```

### Scenario 2 — Alert-Driven RCA (Live)
Start the continuous memory leak data generator:

```bash
bash scripts/demo/start_generator.sh
```

This streams live JVM heap metrics. When heap exceeds 85%, the Kibana alert fires and the Workflow triggers `rca_agent` automatically.

Stop when done:
```bash
bash scripts/demo/stop_generator.sh
```

### Scenario 3 — Distributed System RCA
In Kibana, open the Elastic Workflow for distributed RCA and enter:
```
incident_id: INC0034567
```

---

## Troubleshooting

**`ModuleNotFoundError`** — activate the virtual environment:
```bash
source venv/bin/activate
```

**`ConnectionError`** — check `.env` values:
```bash
python scripts/utilities/test_connectivity.py
```

**No data in Kibana** — re-run ingestion:
```bash
python scripts/data_ingestion/ingest_all_data.py
```

**Python 3.13 issues** — see [PYTHON313_FIX.md](PYTHON313_FIX.md).
