# Agent Development Guide

Reference for understanding, configuring, and extending the `rca_agent` and its ES|QL tools.

---

## Overview

The demo uses a single `rca_agent` built on Elastic AgenticAI. It is backed by Claude Sonnet 4.5 and equipped with 3 specialised ES|QL tools — one per scenario type. The agent adapts its analysis approach based on the incident it receives.

---

## Agent Configuration

Configured in `config/agents.yaml`.

| Parameter | Value |
|---|---|
| Agent name | `rca_agent` |
| LLM | Claude Sonnet 4.5 |
| Max iterations | 10 |
| Output format | PIR document (Executive Summary, Timeline, 5 Whys, Impact, Prevention) |

---

## ES|QL Tools

### Tool 1: `rca_inc_change_logs_infra_traces`
Used for **Scenario 1** (manual RCA — DB connection pool).

Retrieves across: `incidents-servicenow`, `changes-servicenow`, `logs-application`, `logs-infrastructure`, `traces-apm`, `comms-teams`, `comms-email`

**Input parameter:** `incident_id` (string)

**Sample ES|QL:**
```sql
FROM incidents-servicenow, changes-servicenow, logs-application, traces-apm
| WHERE incident_id == ?incident_id
| SORT @timestamp ASC
| LIMIT 500
```

---

### Tool 2: `memory_leak_data_retriever`
Used for **Scenario 2** (alert-driven — JVM memory leak).

Retrieves across: `rca-metrics`, `logs-infrastructure`, `logs-application`, `changes-servicenow`, `rca-alerts`

**Input parameter:** `alert_id` (string)

**Sample ES|QL:**
```sql
FROM rca-metrics, logs-infrastructure, logs-application
| WHERE app_id == ?app_id
  AND @timestamp >= NOW() - 24h
| SORT @timestamp ASC
| LIMIT 500
```

---

### Tool 3: `distributed_system_analyzer`
Used for **Scenario 3** (cascading timeout across multiple services).

Retrieves across: `rca-metrics`, `logs-application`, `traces-apm`, `comms-teams`, `incidents-servicenow`, `rca-alerts`

**Input parameter:** `incident_id` (string)

**Sample ES|QL:**
```sql
FROM rca-metrics, logs-application, traces-apm, comms-teams
| WHERE incident_id == ?incident_id
   OR app_id IN ("APP-9123", "APP-5521", "APP-7654")
| SORT @timestamp ASC
| LIMIT 500
```

---

## Agent System Instructions

The agent's system instructions (in `config/agents.yaml`) define its reasoning approach:

1. **Retrieve** all relevant data using the appropriate ES|QL tool
2. **Correlate** — find temporal relationships between changes, deployments, and error spikes
3. **Trace** — for distributed failures, trace backwards from symptoms to root cause
4. **Analyse** — apply 5 Whys methodology
5. **Generate** — produce a structured PIR document

For distributed failures specifically, the agent is instructed to:
- Identify all affected services
- Build a service dependency map
- Determine which service degraded first (earliest timestamp)
- Check for external dependency failures (third-party APIs, databases)

---

## Extending the Agent

### Adding a new ES|QL tool

1. Define the tool in `config/agents.yaml` under `tools:`
2. Specify the ES|QL query, input parameters, and description
3. Register the tool in your Elastic AI Assistant configuration
4. Reference the tool name in the agent's system instructions

### Adding a new scenario

1. Generate synthetic data (see [DATA_GENERATION_GUIDE.md](DATA_GENERATION_GUIDE.md))
2. Ingest data into the appropriate indices
3. Create or reuse an ES|QL tool that covers the new index pattern
4. Add scenario parameters to `config/scenarios.yaml`
5. Create a corresponding Elastic Workflow in Kibana

### Modifying the PIR output format

The output structure is defined in the agent's system instructions in `config/agents.yaml`. Modify the `output_format` section to change section headings, add new fields, or change the document structure.

---

## Data Flow

```
Trigger (manual or alert)
        ↓
Elastic Workflow activates rca_agent
        ↓
Agent selects appropriate ES|QL tool based on incident type
        ↓
Tool queries Elasticsearch (returns structured JSON)
        ↓
Agent reasons over results (Claude Sonnet 4.5)
        ↓
Agent generates PIR document
        ↓
Workflow posts to ServiceNow (via Pipedream) + logs to knowledge base
```
