# Elastic Agentic RCA Demo

> **Autonomous Root Cause Analysis using Elastic AgenticAI + Elastic Workflows**

An end-to-end demo of autonomous incident root cause analysis built entirely on the Elastic Stack. A single `rca_agent` powered by Claude Sonnet 4.5 investigates production incidents by correlating logs, metrics, APM traces, ITSM tickets, and team communications — completing a full RCA in under 3 minutes.

---

## What This Demo Shows

| Scenario | Trigger | Root Cause | Docs Analyzed |
|---|---|---|---|
| **1 – Manual RCA** | Engineer inputs incident ID | DB connection pool: `max_connections` changed 100→50 | 156 |
| **2 – Alert-Driven RCA** | Kibana alert: JVM heap > 85% | Memory leak in PaymentService cache config | 180 |
| **3 – Distributed RCA** | Kibana alert: order gateway errors | Stripe API slowness cascading 3 layers upstream | 228+ |

**564+ documents ingested and analyzed across all scenarios**

---

## Architecture

```
  Manual Trigger                    Kibana Alert
  (Incident ID)                  (e.g. heap > 85%)
        │                                │
        └──────────────┬─────────────────┘
                       │
              ┌────────▼────────┐
              │  Elastic        │
              │  Workflow       │
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
                       │
        ┌──────────────▼──────────────────────────────┐
        │              Elasticsearch                   │
        │         (564+ documents ingested)            │
        │  incidents │ logs │ metrics │ traces │ comms │
        │         knowledge base (ELSER)               │
        └──────────────┬──────────────────────────────┘
                       │
          ┌────────────┴────────────┐
          │                         │
   ┌──────▼──────┐         ┌────────▼────────┐
   │  ServiceNow │         │   PIR Document  │
   │  (Pipedream)│         │   (RCA output)  │
   └─────────────┘         └─────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/your-org/elastic-agentic-rca-demo.git
cd elastic-agentic-rca-demo
cp .env.example .env          # Fill in your Elastic credentials
pip install -r requirements.txt
python scripts/utilities/setup_elasticsearch.py
python scripts/data_ingestion/ingest_all_data.py
```

See [QUICKSTART.md](QUICKSTART.md) for the full walkthrough.

---

## Tech Stack

| Component | Technology |
|---|---|
| Search & Analytics | Elasticsearch 9.2+ |
| Observability & Alerting | Kibana 9.2+ |
| AgenticAI + Workflows | Elastic native |
| Agent Query Tools | ES\|QL (3 tools) |
| LLM | Claude Sonnet 4.5 |
| Semantic Search / RAG | ELSER |
| ITSM Integration | ServiceNow via Pipedream |

---

## Documentation

| Doc | Description |
|---|---|
| [QUICKSTART.md](QUICKSTART.md) | Setup, ingest, verify — get running in 15 minutes |
| [DATA_GENERATION_GUIDE.md](DATA_GENERATION_GUIDE.md) | Regenerate synthetic data for all 3 scenarios |
| [AGENT_DEVELOPMENT_GUIDE.md](AGENT_DEVELOPMENT_GUIDE.md) | Extend or modify the rca_agent and ES\|QL tools |
| [SCENARIO3_BUILD_PLAN.md](SCENARIO3_BUILD_PLAN.md) | Distributed system scenario reference |

---

## License

Apache 2.0 — see [LICENSE](LICENSE).
