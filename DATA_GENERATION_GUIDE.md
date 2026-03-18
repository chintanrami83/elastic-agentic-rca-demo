# Data Generation Guide

The `data/synthetic/` directory contains pre-generated data for all 3 scenarios. This guide explains how to regenerate it, what it contains, and how to verify it in Kibana.

---

## Pre-Generated Data

All data is already included in the repo. To ingest it directly without regenerating:

```bash
source venv/bin/activate
python scripts/data_ingestion/ingest_all_data.py
```

---

## Regenerating Synthetic Data

If you need to regenerate the data (e.g. with updated timestamps):

```bash
source venv/bin/activate

# Regenerate all scenarios
python scripts/data_generation/generate_all_scenarios.py

# Or individual scenarios
python scripts/data_generation/generate_scenario2_memory_leak.py
python scripts/data_generation/generate_scenario3_cascading_timeout.py
```

Then re-ingest:
```bash
python scripts/data_ingestion/ingest_all_data.py
```

---

## Scenario 1 — DB Connection Pool Exhaustion

**Incident:** `INC0012345` | **App:** `CustomerPortal-API (APP-2847)`

**Timeline:** Feb 8, 2026 01:45–04:15 AEDT

| Data Type | Count | Index |
|---|---|---|
| Incident record | 1 | `incidents-servicenow` |
| Change records | 2 | `changes-servicenow` |
| Application logs | 42 | `logs-application` |
| Infrastructure logs | 15 | `logs-infrastructure` |
| APM traces | 27 | `traces-apm` |
| Teams messages | 3 | `comms-teams` |
| Emails | 2 | `comms-email` |
| KB articles | 1 | `knowledge-base` |

**Root cause embedded in data:** Deployment at 01:45 changed `max_connections` from 100 → 50. Errors begin 30 minutes later.

**Kibana verification:**
```
incident_id:"INC0012345"
```
Time range: Feb 8, 2026 01:00–05:00

---

## Scenario 2 — JVM Memory Leak

**Incident:** `INC0023456` | **App:** `PaymentService API (APP-9123)`

**Timeline:** Feb 4, 2026 11:00–13:00 AEDT

| Data Type | Count | Index |
|---|---|---|
| Incident record | 1 | `incidents-servicenow` |
| Change record | 1 | `changes-servicenow` |
| Application logs | 10 | `logs-application` |
| GC logs | 28 | `logs-infrastructure` |
| JVM heap metrics | 67 | `rca-metrics` |
| APM traces | 15 | `traces-apm` |
| Teams messages | 4 | `comms-teams` |
| KB articles | 1 | `knowledge-base` |
| Alerts | 2 | `rca-alerts` |

**Root cause embedded in data:** Cache configuration change 8 hours before alert causes heap to grow from 45% → 87.3% with OutOfMemoryError.

**Kibana verification:**
```
incident_id:"INC0023456"
```
Time range: Feb 4, 2026 10:00–14:00

**Key metrics to observe in Discover:**
- `heap_percent` trending from ~45% to 87.3%
- `gc_pause_ms` increasing over time
- `OutOfMemoryError` in application logs

---

## Scenario 3 — Cascading Timeout (Distributed)

**Incident:** `INC0034567` | **Services:** 3 microservices

**Timeline:** Feb 3, 2026 14:00–16:15 AEDT

| Service | App ID | Role |
|---|---|---|
| PaymentService | `APP-9123` | Root cause — Stripe API slowness |
| InventoryService | `APP-5521` | Timeout waiting for Payment |
| OrderProcessing Gateway | `APP-7654` | Failures waiting for Inventory |

| Data Type | Count | Index |
|---|---|---|
| Incident record | 1 | `incidents-servicenow` |
| Application logs | 28 | `logs-application` |
| Metrics (3 services) | 135 | `rca-metrics` |
| Distributed traces | 27 | `traces-apm` |
| Teams messages | 5 | `comms-teams` |
| Alerts | 2 | `rca-alerts` |
| KB articles | 1 | `knowledge-base` |

**Root cause embedded in data:** Stripe API latency degrades PaymentService at 14:03 → InventoryService timeouts at 14:05 → OrderProcessing failures at 14:08.

**Kibana verification:**
```
incident_id:"INC0034567"
```
Time range: Feb 3, 2026 13:30–17:00

**Cascading pattern to observe:**
- `APP-9123` response times spike first (14:03)
- `APP-5521` timeouts follow (14:05)
- `APP-7654` error rate spikes last (14:08)

---

## Verifying All Data Loaded

Run in Kibana Discover with index pattern `rca-*`:

```
# Check total document count per scenario
incident_id:*
```

Expected totals:
- Scenario 1: ~156 documents
- Scenario 2: ~180 documents
- Scenario 3: ~228 documents
- **Grand total: 564+ documents**

---

## Data Location

```
data/synthetic/
├── incidents/            scenario1_incidents.json
├── changes/              scenario1_changes.json
├── logs/                 scenario1_logs_app.json
│                         scenario1_logs_infra.json
├── traces/               scenario1_traces.json
├── comms/                scenario1_teams.json
│                         scenario1_emails.json
├── knowledge/            scenario1_kb.json
├── scenario2_memory_leak/
│   ├── alerts/           alert_1.json, alert_2.json
│   ├── changes/          CHG0098765.json
│   ├── incidents/        INC0023456.json
│   ├── knowledge/        KB-8934.json
│   ├── logs/app/         application_logs.json
│   ├── logs/infra/       gc_logs.json
│   ├── metrics/          jvm_heap_metrics.json
│   └── traces/           apm_traces.json
└── scenario3_cascading_timeout/
    ├── alerts/           alerts.json
    ├── comms/teams/      teams_messages.json
    ├── incidents/        incident.json
    ├── knowledge/        kb_cascading_timeouts.json
    ├── logs/app/         inventory_service_logs.json
    │                     order_gateway_logs.json
    │                     payment_service_logs.json
    ├── metrics/          inventory_service_metrics.json
    │                     order_gateway_metrics.json
    │                     payment_service_metrics.json
    └── traces/           distributed_traces.json
```
