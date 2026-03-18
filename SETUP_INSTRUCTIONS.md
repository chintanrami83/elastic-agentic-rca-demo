# Setup Instructions

Full reference for configuring the demo environment from scratch.

---

## Requirements

| Requirement | Version |
|---|---|
| Python | 3.11 or 3.12 (see PYTHON313_FIX.md for 3.13) |
| Elasticsearch | 9.2+ |
| Kibana | 9.2+ |
| ELSER model | Deployed on your cluster |

---

## Environment Configuration

Copy the template and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `ELASTIC_URL` | Your Elasticsearch endpoint |
| `ELASTIC_USERNAME` | Cluster username (default: `elastic`) |
| `ELASTIC_PASSWORD` | Cluster password |
| `ELASTIC_API_KEY` | Alternative to username/password |
| `KIBANA_URL` | Your Kibana endpoint |
| `ELSER_MODEL_ID` | ELSER model ID (default: `.elser_model_2_linux-x86_64`) |

---

## Installation

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

For a minimal install (fewer dependencies):
```bash
pip install -r requirements-minimal.txt
```

---

## Elasticsearch Setup

### Test connectivity first
```bash
python scripts/utilities/test_connectivity.py
```

### Create all indices and mappings
```bash
python scripts/utilities/setup_elasticsearch.py
```

This creates the following indices with correct field mappings:

| Index | Contains |
|---|---|
| `incidents-servicenow` | Incident records |
| `changes-servicenow` | Change and deployment records |
| `logs-application` | Application error logs |
| `logs-infrastructure` | Infrastructure and GC logs |
| `traces-apm` | Distributed APM traces |
| `comms-teams` | Microsoft Teams messages |
| `comms-email` | Email communications |
| `knowledge-base` | KB articles (ELSER indexed) |
| `rca-metrics` | JVM, CPU, connection pool metrics |
| `rca-alerts` | Kibana alert records |

---

## Data Ingestion

Synthetic data for all 3 scenarios is pre-generated in `data/synthetic/`. Ingest it with:

```bash
source venv/bin/activate
python scripts/data_ingestion/ingest_all_data.py
```

To ingest individual scenarios:
```bash
python scripts/data_ingestion/ingest_scenario2_data.py   # Memory leak
python scripts/data_ingestion/ingest_scenario3_data.py   # Cascading timeout
```

---

## Kibana Configuration

After ingestion, set up Kibana to explore the data:

1. **Discover → Data Views → Create data view**
   - Index pattern: `rca-*`
   - Time field: `@timestamp`

2. **Verify each scenario loads** (see [QUICKSTART.md](QUICKSTART.md) for verification queries)

---

## Elastic Workflow Setup

The `rca_agent` is triggered via an Elastic Workflow. To configure:

1. Go to **Kibana → Workflows**
2. Import or create a workflow using the definition in `config/rca_workflow.yaml`
3. Configure the agent with system instructions from `config/agents.yaml`
4. Set up the 3 ES|QL tools defined in `config/agents.yaml`

### Alert-Driven Trigger (Scenario 2)

Create a Kibana alerting rule:
- **Index:** `rca-metrics`
- **Condition:** `avg(heap_percent) > 85` over last 5 minutes
- **Action:** Trigger the RCA workflow with the alert context

---

## ServiceNow Integration (Optional)

Scenario 2 and 3 workflows create ServiceNow incidents via Pipedream. To enable:

1. Set up a Pipedream workflow that accepts a POST request and creates a ServiceNow incident
2. Update the webhook URL in `config/rca_workflow.yaml`

This step is optional — the RCA analysis runs fully without it.

---

## Verify Everything Works

```bash
# 1. Connectivity
python scripts/utilities/test_connectivity.py

# 2. Document counts
# In Kibana Discover with index pattern rca-*:
# incident_id:"INC0012345"  → ~156 docs  (Scenario 1)
# incident_id:"INC0023456"  → ~180 docs  (Scenario 2)
# incident_id:"INC0034567"  → ~228 docs  (Scenario 3)
```
