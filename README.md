# Elastic Agentic RCA Demo

> **Autonomous Root Cause Analysis using Elastic AgenticAI + Elastic Workflows**

This repository demonstrates an end-to-end Agentic AI system for automated incident root cause analysis (RCA) built entirely on the Elastic Stack. It showcases how Elastic's native AgenticAI framework and Workflow automation — powered by Claude Sonnet 4.5 as the LLM — can autonomously investigate production incidents by correlating logs, metrics, APM traces, ITSM data, and team communications.

Originally built as a proof-of-concept for a banking enterprise, this demo is fully reproducible on any Elastic Cloud deployment (v9.2+).

---

## 🎯 What This Demo Shows

| Scenario | Trigger | Root Cause | Documents Analyzed |
|---|---|---|---|
| **Scenario 1** – Manual RCA | Engineer inputs incident ID | DB connection pool: `max_connections` changed 100→50 | 156 |
| **Scenario 2** – Alert-Driven RCA | Kibana alert: JVM heap > 85% | Memory leak in PaymentService cache config | 180 |
| **Scenario 3** – Distributed RCA | Kibana alert: order gateway errors | Stripe API slowness cascading 3 layers upstream | 228+ |

**Total: 564+ documents ingested and analyzed across all scenarios**

The system demonstrates:
- **Fully autonomous operation** — alert fires → AI investigates → ServiceNow incident created, zero human intervention
- **Single intelligent agent** — one `rca_agent` adapts its analysis approach per incident type
- **Multi-signal correlation** — 7+ data sources analyzed simultaneously
- **3-minute RCA** — complete root cause analysis consistently under 3 minutes
- **PIR generation** — structured Post-Incident Review output ready for stakeholders

---

## 🏗️ Architecture

Everything runs natively inside Elastic — no external orchestration framework required.

```
  Manual Trigger                    Kibana Alert
  (Incident ID)                  (e.g. heap > 85%)
        │                                │
        └──────────────┬─────────────────┘
                       │
              ┌────────▼────────┐
              │  Elastic        │
              │  Workflow       │  ← Trigger: Manual or Alert-driven
              └────────┬────────┘
                       │
              ┌────────▼────────────────────────────┐
              │           rca_agent                 │
              │     (Elastic AgenticAI)             │
              │     LLM: Claude Sonnet 4.5          │
              │                                     │
              │  Tool 1: rca_inc_change_logs_       │
              │           infra_traces   (ES|QL)    │
              │  Tool 2: memory_leak_data_          │
              │           retriever      (ES|QL)    │
              │  Tool 3: distributed_system_        │
              │           analyzer       (ES|QL)    │
              └────────┬────────────────────────────┘
                       │  queries
        ┌──────────────▼──────────────────────────────┐
        │              Elasticsearch                   │
        │         (564+ documents ingested)            │
        │                                              │
        │  incidents  │  logs      │  metrics          │
        │  changes    │  traces    │  comms            │
        │  knowledge base (ELSER semantic search)      │
        └──────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼──────┐         ┌────────▼────────┐
   │  ServiceNow │         │   PIR Document  │
   │  (via       │         │   (structured   │
   │  Pipedream) │         │   RCA output)   │
   └─────────────┘         └─────────────────┘
```

### Key Design Decisions

| Decision | Detail |
|---|---|
| **Single agent** | One `rca_agent` with 3 specialised ES\|QL tools — not multiple agents |
| **LLM** | Claude Sonnet 4.5 — advanced reasoning, natural language log/metric analysis |
| **Tools** | ES\|QL queries — fast, precise retrieval from Elasticsearch indices |
| **Trigger** | Manual (incident ID input) or Alert-driven (Kibana webhook → Workflow) |
| **Output** | PIR document + ServiceNow incident (via Pipedream integration) |
| **Semantic search** | ELSER for knowledge base RAG lookups |

---

## 📊 Data Sources (7+)

| Source | Index | Used For |
|---|---|---|
| ServiceNow Incidents | `incidents-servicenow` | Business context, severity, timeline |
| Application Logs | `logs-app-*` | Error patterns, stack traces |
| Infrastructure Logs | `logs-infra-*` | System events, GC logs |
| Metrics | `metrics-*` | CPU, memory, connections, response times |
| APM / Distributed Traces | `traces-apm-*` | Service dependencies, latency |
| Communications | `comms-teams`, `comms-email` | Teams messages, email threads |
| Change Records | `changes-servicenow` | Deployments, config changes |
| Knowledge Base | `knowledge-base` | Historical patterns, prior solutions (ELSER) |

---

## 📁 Repository Structure

```
elastic-agentic-rca-demo/
├── .env.example                   # Environment variable template
├── .gitignore
├── LICENSE
├── README.md
├── QUICKSTART.md                  # 15-minute setup guide
├── SETUP_INSTRUCTIONS.md          # Full step-by-step setup
├── AGENT_DEVELOPMENT_GUIDE.md     # How to build / extend the agent & tools
├── DATA_GENERATION_GUIDE.md       # How to regenerate synthetic data
├── SCENARIO3_BUILD_PLAN.md        # Distributed tracing scenario detail
├── PYTHON313_FIX.md               # Python 3.13 compatibility notes
│
├── config/
│   ├── elastic.yaml               # Elasticsearch index + cluster config
│   ├── agents.yaml                # rca_agent configuration
│   ├── rca_workflow.yaml          # Workflow step definitions
│   └── scenarios.yaml             # Demo scenario parameters
│
├── agents/
│   └── data_retriever/
│       └── agent.py               # ES|QL query layer (no LLM)
│
├── scripts/
│   ├── utilities/
│   │   ├── es_client.py           # Elasticsearch client factory
│   │   ├── setup_elasticsearch.py # Index + mapping setup
│   │   └── test_connectivity.py   # Pre-flight connectivity check
│   ├── data_generation/
│   │   ├── generate_all_scenarios.py
│   │   ├── generate_scenario2_memory_leak.py
│   │   └── generate_scenario3_cascading_timeout.py
│   ├── data_ingestion/
│   │   ├── ingest_all_data.py
│   │   ├── ingest_scenario2_data.py
│   │   └── ingest_scenario3_data.py
│   └── demo/
│       ├── continuous_memory_leak_generator.py  # Live data for Scenario 2
│       ├── start_generator.sh
│       ├── stop_generator.sh
│       └── README_GENERATOR.md
│
├── data/
│   └── synthetic/
│       ├── scenario1_*/           # DB connection pool exhaustion (156 docs)
│       ├── scenario2_memory_leak/ # JVM memory leak → OOM (180 docs)
│       └── scenario3_cascading_timeout/ # Distributed cascade (228+ docs)
│
└── outputs/
    ├── pir_documents/             # Generated PIR Word docs (git-ignored)
    └── reports/                   # Generated JSON reports (git-ignored)
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or 3.12 (see `PYTHON313_FIX.md` for 3.13 notes)
- Elastic Cloud deployment v9.2+ (or self-managed)
- ELSER model deployed on your cluster
- Pipedream account (for ServiceNow integration, optional)

### 1. Clone & configure

```bash
git clone https://github.com/your-org/elastic-agentic-rca-demo.git
cd elastic-agentic-rca-demo

cp .env.example .env
# Edit .env with your Elastic Cloud credentials
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set up Elasticsearch

```bash
python scripts/utilities/test_connectivity.py
python scripts/utilities/setup_elasticsearch.py
```

### 4. Ingest demo data

```bash
# All scenarios at once
python scripts/data_ingestion/ingest_all_data.py

# Or individual scenarios
python scripts/data_ingestion/ingest_scenario2_data.py
python scripts/data_ingestion/ingest_scenario3_data.py
```

### 5. Run a scenario

```bash
# Start the live memory leak data generator (Scenario 2 - Alert-Driven)
bash scripts/demo/start_generator.sh

# Stop it when done
bash scripts/demo/stop_generator.sh
```

For the full walkthrough including Kibana Workflow setup and `rca_agent` configuration, see **[QUICKSTART.md](QUICKSTART.md)**.

---

## 📊 Demo Scenarios In Detail

### Scenario 1 — Manual RCA (Database Connection Pool)
- **Trigger:** Engineer manually inputs incident ID `INC0012345` into the Elastic Workflow
- **Data analyzed:** 42 app logs, 67 metrics, 1 deployment record, 27 distributed traces, 3 Teams messages (156 total)
- **Root cause:** Deployment at 2:15 PM changed `max_connections` from 100 → 50, causing pool exhaustion
- **Demo value:** Shows `rca_agent` correlating deployment timing with error patterns automatically

### Scenario 2 — Alert-Driven RCA (JVM Memory Leak)
- **Trigger:** Kibana alert fires on `heap_percent > 85%` at midnight → Workflow activates automatically
- **Data analyzed:** 67 memory metrics, 28 GC logs, 10 app logs, 1 deployment record (180 total)
- **Root cause:** Memory leak in `PaymentService` introduced by cache configuration change 8 hours prior
- **Demo value:** Full autonomy — alert → investigation → ServiceNow incident → team notification, zero human intervention

### Scenario 3 — Distributed System RCA (Cascading Timeouts)
- **Trigger:** Kibana alert on Order Processing Gateway error rate spike
- **Data analyzed:** 28 app logs, 27 distributed traces, metrics across 3 services, 5 Teams messages (228+ total)
- **Service chain:** `Customer Request → Order Processing ← Inventory ← Payment ← Stripe API (root cause)`
- **Root cause:** Stripe API latency causing slowness 3 layers deep — symptoms in Order Processing, root cause at Stripe
- **Demo value:** Where AI excels — tracing backwards through distributed service dependencies humans struggle to map manually

---

## 🔧 Agent & Tool Configuration

The `rca_agent` and its 3 ES|QL tools are configured in `config/agents.yaml`. Key parameters:

| Parameter | Description |
|---|---|
| `llm.model` | `claude-sonnet-4-5` |
| `tools[0]` | `rca_inc_change_logs_infra_traces` — Scenario 1 |
| `tools[1]` | `memory_leak_data_retriever` — Scenario 2 |
| `tools[2]` | `distributed_system_analyzer` — Scenario 3 |
| `workflow.trigger` | `manual` or `alert` |
| `output.format` | PIR: Executive Summary, Timeline, 5 Whys, Impact, Prevention |

---

## 🛡️ Security Notes

- **Never commit `.env`** — it is listed in `.gitignore`
- Use **API keys** rather than username/password for production
- Rotate Elastic credentials used for this demo after the POC
- The `credentials-*.csv` file from Elastic Cloud is excluded in `.gitignore`

---

## 📚 Documentation

| Document | Description |
|---|---|
| [QUICKSTART.md](QUICKSTART.md) | 15-minute setup including Kibana Workflow config |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Full setup reference |
| [AGENT_DEVELOPMENT_GUIDE.md](AGENT_DEVELOPMENT_GUIDE.md) | Building and extending the rca_agent and ES\|QL tools |
| [DATA_GENERATION_GUIDE.md](DATA_GENERATION_GUIDE.md) | Synthetic data generation |
| [SCENARIO3_BUILD_PLAN.md](SCENARIO3_BUILD_PLAN.md) | Distributed scenario architecture detail |

---

## 🧩 Tech Stack

| Component | Technology |
|---|---|
| Search & Analytics | Elasticsearch 9.2+ |
| Observability & Alerting | Kibana 9.2+ |
| AgenticAI Framework | Elastic AgenticAI (native) |
| Workflow Automation | Elastic Workflows (native) |
| Agent Query Tools | ES\|QL (3 specialised tools) |
| LLM | Claude Sonnet 4.5 (via Anthropic API) |
| Semantic Search / RAG | ELSER (Elastic Learned Sparse EncodeR) |
| ITSM Integration | ServiceNow via Pipedream |
| Data Ingestion | Python + elasticsearch-py |

---

## 📝 License

Apache 2.0 — see [LICENSE](LICENSE).
