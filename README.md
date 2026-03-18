# Elastic Agentic RCA Demo

> **Autonomous Root Cause Analysis using Elastic AgenticAI + Kibana Workflows**

This repository demonstrates an end-to-end Agentic AI system for automated incident root cause analysis (RCA) built on the Elastic Stack. It showcases how Elastic's AgenticAI capabilities — combined with Claude.ai workflows — can autonomously investigate production incidents by correlating logs, metrics, APM traces, ITSM data, and team communications.

Originally built as a proof-of-concept for a banking enterprise, this demo is designed to be fully reproducible on any Elastic Cloud deployment (v9.2+).

---

## 🎯 What This Demo Shows

| Scenario | Description | Key Signal |
|---|---|---|
| **Scenario 1** – Manual RCA | Engineer triggers RCA on a known incident ID | ServiceNow incident + log correlation |
| **Scenario 2** – Alert-Driven RCA | Kibana alert fires → autonomous investigation begins | JVM memory leak → OOM → payment failures |
| **Scenario 3** – Distributed RCA | Cascading timeout across 3 microservices | Inventory → Order Gateway → Payment Service |

The system demonstrates:
- **Autonomous agent orchestration** — multiple specialised agents working in sequence
- **Multi-signal correlation** — logs, metrics, APM traces, ITSM tickets, Teams/email comms
- **RAG-powered reasoning** — knowledge base lookups via ELSER semantic search
- **Post-Incident Review (PIR) generation** — structured output documents

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────────┐
                    │     Claude.ai Workflow           │
                    │  (Orchestrator / Entry Point)    │
                    └──────────────┬──────────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
    ┌─────────▼──────┐  ┌──────────▼──────┐  ┌────────▼────────┐
    │ Data Retriever │  │  Observability  │  │  Comms Agent    │
    │    Agent       │  │     Agent       │  │ (Teams/Email)   │
    └─────────┬──────┘  └──────────┬──────┘  └────────┬────────┘
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Correlation & RCA Agent    │
                    │  (5 Whys + ELSER RAG)        │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │    PIR Generator Agent       │
                    │  (Structured Report Output)  │
                    └─────────────────────────────┘

    All agents query ──► Elasticsearch (logs, metrics, traces, ITSM, KB)
    Alerts trigger  ──► Kibana Alerting → Webhook → Workflow entry
```

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
├── AGENT_DEVELOPMENT_GUIDE.md     # How to build / extend agents
├── DATA_GENERATION_GUIDE.md       # How to regenerate synthetic data
├── SCENARIO3_BUILD_PLAN.md        # Distributed tracing scenario detail
├── PYTHON313_FIX.md               # Python 3.13 compatibility notes
│
├── config/
│   ├── elastic.yaml               # Elasticsearch index + cluster config
│   ├── agents.yaml                # Agent configuration (LLM, timeouts)
│   ├── rca_workflow.yaml          # Workflow step definitions
│   └── scenarios.yaml             # Demo scenario definitions
│
├── agents/
│   └── data_retriever/
│       └── agent.py               # Agent 1: Pure ES query agent (no LLM)
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
│       ├── continuous_memory_leak_generator.py
│       ├── start_generator.sh
│       ├── stop_generator.sh
│       └── README_GENERATOR.md
│
├── data/
│   └── synthetic/
│       ├── scenario1_*/           # DB connection pool exhaustion
│       ├── scenario2_memory_leak/ # JVM memory leak → OOM
│       └── scenario3_cascading_timeout/ # Distributed service cascade
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
# Start the live memory leak data generator (Scenario 2)
bash scripts/demo/start_generator.sh

# Stop it
bash scripts/demo/stop_generator.sh
```

For the full walkthrough, see **[QUICKSTART.md](QUICKSTART.md)**.

---

## 📊 Demo Scenarios In Detail

### Scenario 1 — Manual RCA (Database Connection Pool)
- **Trigger:** Engineer manually inputs incident ID `INC0012345`
- **Data sources:** ServiceNow incident, application logs, infra logs, APM traces, change records
- **Root cause:** Connection pool exhaustion after scheduled job change deploys too many threads
- **Output:** 5 Whys analysis + PIR document

### Scenario 2 — Alert-Driven RCA (JVM Memory Leak)
- **Trigger:** Kibana alert fires on `heap_percent > 85%`
- **Data sources:** JVM metrics, GC logs, APM traces, Teams messages, change `CHG0098765`
- **Root cause:** Memory leak in `PaymentService` introduced by cache configuration change
- **Output:** Autonomous alert → investigation → PIR without human intervention

### Scenario 3 — Distributed System RCA (Cascading Timeouts)
- **Trigger:** Kibana alert on order gateway error rate
- **Services involved:** `InventoryService` → `OrderGateway` → `PaymentService`
- **Data sources:** Distributed traces, per-service metrics, Teams war-room messages
- **Root cause:** Database slow query on inventory table causes upstream cascade
- **Output:** Cross-service timeline + impact analysis + PIR

---

## 🔧 Configuration

All agent behaviour is controlled via YAML files in `config/`:

| File | Controls |
|---|---|
| `elastic.yaml` | Index names, cluster settings, field mappings |
| `agents.yaml` | LLM model selection, timeouts, retry behaviour |
| `rca_workflow.yaml` | Step sequence, agent hand-offs, output format |
| `scenarios.yaml` | Demo scenario parameters and expected outputs |

---

## 🛡️ Security Notes

- **Never commit `.env`** — it is listed in `.gitignore`
- Use **API keys** rather than username/password for production deployments
- Rotate the Elastic credentials used for this demo after completing the POC
- The `credentials-*.csv` file from Elastic Cloud should never be committed — it is also excluded in `.gitignore`

---

## 📚 Documentation

| Document | Description |
|---|---|
| [QUICKSTART.md](QUICKSTART.md) | 15-minute setup guide |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Full setup reference |
| [AGENT_DEVELOPMENT_GUIDE.md](AGENT_DEVELOPMENT_GUIDE.md) | Building and extending agents |
| [DATA_GENERATION_GUIDE.md](DATA_GENERATION_GUIDE.md) | Synthetic data generation |
| [SCENARIO3_BUILD_PLAN.md](SCENARIO3_BUILD_PLAN.md) | Distributed scenario architecture |

---

## 🧩 Tech Stack

| Component | Technology |
|---|---|
| Search & Analytics | Elasticsearch 9.2+ |
| Observability UI | Kibana 9.2+ |
| Semantic Search | ELSER (Elastic Learned Sparse EncodeR) |
| Agent Orchestration | Claude.ai Workflows |
| LLM | Claude (via Anthropic API) |
| Data Ingestion | Python + elasticsearch-py |
| APM / Tracing | Elastic APM (EDOT/OpenTelemetry) |

---

## 📝 License

Apache 2.0 — see [LICENSE](LICENSE).
