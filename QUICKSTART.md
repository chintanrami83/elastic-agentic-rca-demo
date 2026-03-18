# Quick Start Guide

Get the demo running in your environment in 15 minutes.

---

## Prerequisites

- Python 3.11 or 3.12
- Elastic Cloud deployment v9.2+ with ELSER model deployed
- Git

---

## Step 1 — Clone and Configure

```bash
git clone https://github.com/your-org/elastic-agentic-rca-demo.git
cd elastic-agentic-rca-demo
cp .env.example .env
```

Edit `.env` and fill in your Elastic Cloud credentials:

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
pip install -r requirements.txt
```

---

## Step 3 — Test Connectivity

```bash
python scripts/utilities/test_connectivity.py
```

Expected output:
```
✓ Connected to Elasticsearch 9.x.x
✓ ELSER model found
✓ Kibana reachable
```

If this fails, double-check your `.env` values and that your cluster is running.

---

## Step 4 — Create Elasticsearch Indices

```bash
python scripts/utilities/setup_elasticsearch.py
```

This creates all required indices:
```
✓ incidents-servicenow
✓ changes-servicenow
✓ logs-application
✓ logs-infrastructure
✓ traces-apm
✓ comms-teams
✓ comms-email
✓ knowledge-base
✓ rca-metrics
✓ rca-alerts
```

---

## Step 5 — Ingest Demo Data

```bash
# Ingest all 3 scenarios at once
python scripts/data_ingestion/ingest_all_data.py

# Or ingest individual scenarios
python scripts/data_ingestion/ingest_scenario2_data.py
python scripts/data_ingestion/ingest_scenario3_data.py
```

Expected output:
```
✓ Scenario 1: 156 documents indexed
✓ Scenario 2: 180 documents indexed
✓ Scenario 3: 228 documents indexed
Total: 564 documents ingested
```

---

## Step 6 — Verify in Kibana

1. Open Kibana → **Discover**
2. Create a data view with index pattern `rca-*` and time field `@timestamp`
3. Run these searches to confirm data loaded correctly:

**Scenario 1 — DB Connection Pool:**
```
incident_id:"INC0012345"
```
Expected: ~156 documents

**Scenario 2 — Memory Leak:**
```
incident_id:"INC0023456"
```
Expected: ~180 documents

**Scenario 3 — Cascading Timeout:**
```
incident_id:"INC0034567"
```
Expected: ~228 documents

---

## Step 7 — Run the Demo

### Scenario 2 — Live Alert-Driven RCA (recommended starting point)

Start the continuous memory leak data generator to trigger a real Kibana alert:

```bash
bash scripts/demo/start_generator.sh
```

This streams live JVM heap metrics into Elasticsearch. Once heap exceeds 85%, your Kibana alert fires and the Elastic Workflow activates the `rca_agent` automatically.

Stop the generator when done:
```bash
bash scripts/demo/stop_generator.sh
```

---

## Troubleshooting

**`ModuleNotFoundError`** — virtual environment not activated:
```bash
source venv/bin/activate
```

**`ConnectionError`** — check `.env` credentials and that your cluster is reachable:
```bash
python scripts/utilities/test_connectivity.py
```

**No data in Kibana** — re-run ingestion:
```bash
python scripts/data_ingestion/ingest_all_data.py
```

**Python 3.13 issues** — see [PYTHON313_FIX.md](PYTHON313_FIX.md).
