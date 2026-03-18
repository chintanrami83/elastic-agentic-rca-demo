# Elastic AgenticAI RCA System - Development Guide

## 🎯 What We're Building

**Complete automated RCA system using Elastic 9.3 AgenticAI + Workflow**

---

## 📦 Phase 1: AGENT 1 - Data Retriever (✅ READY TO TEST)

### What It Does
Pure tool-based agent that queries Elasticsearch for all incident-related data.

**NO LLM** - just intelligent queries using:
- Elasticsearch Query API
- Time range calculations
- Multi-index searches

### Retrieves
1. Incident record from `rca-incidents`
2. Related changes from `rca-changes` (by app_id + time window)
3. Application logs from `rca-logs-app` (errors during incident)
4. Infrastructure logs from `rca-logs-infra` (system metrics)
5. APM traces from `rca-traces` (slow transactions)
6. Teams messages from `rca-comms-teams` (investigation)
7. Emails from `rca-comms-email` (alerts)

### Time Window Logic
```
Start: 24 hours BEFORE incident creation
End: Incident resolution time (or +6 hours if ongoing)
```

This captures:
- ✅ Changes that happened before incident
- ✅ All errors during incident
- ✅ Resolution activities
- ✅ Human investigation (Teams/Email)

---

## 🧪 Test Agent 1 NOW

### Step 1: Download Files

Download these 3 files (above):
1. `agents/data_retriever/agent.py`
2. `agents/data_retriever/__init__.py`
3. `config/rca_workflow.yaml` (workflow definition for reference)

Place in:
```
/path/to/elastic-agentic-rca-demo/
├── agents/
│   └── data_retriever/
│       ├── __init__.py
│       └── agent.py
└── config/
    └── rca_workflow.yaml
```

### Step 2: Make Executable

```bash
cd /path/to/elastic-agentic-rca-demo
chmod +x agents/data_retriever/agent.py
```

### Step 3: Run Agent 1

```bash
source venv/bin/activate
python agents/data_retriever/agent.py --incident INC0012345
```

### Expected Output

```
🤖 Agent 1: Data Retriever
Retrieving data for INC0012345...

⠋ Retrieving incident record...
  ✓ Found incident: CustomerPortal API returning 500 errors - connection...
  ✓ Time window: 2026-02-04 08:00 AEDT → 2026-02-04 11:00 AEDT
  ✓ Found 2 change(s)
  ✓ Found 268 application log(s)
  ✓ Found 23 infrastructure log(s)
  ✓ Found 231 trace(s)
  ✓ Found 8 communication(s)

✓ Data retrieval complete
Total documents: 533

📊 Summary:
  Incident: INC0012345
  Application: APP-2847
  Severity: P1
  Changes found: 2
  Total logs: 291
  Traces: 231
  Communications: 8

✓ Agent 1 execution successful!
```

---

## 🏗️ Complete Architecture

### Workflow (Elastic Orchestration)
```
Input: incident_id = "INC0012345"
  ↓
┌─────────────────────────────────────┐
│  STEP 1: Data Retrieval             │
│  Agent: DataRetrieverAgent          │
│  Type: Tool-based (no LLM)          │
│  Time: ~2 minutes                   │
└─────────────────────────────────────┘
  ↓ passes: incident_data
┌─────────────────────────────────────┐
│  STEP 2: Temporal Correlation       │
│  Agent: CorrelationAgent            │
│  Type: LLM + Tools                  │
│  LLM: Claude Sonnet 4               │
│  Time: ~1 minute                    │
└─────────────────────────────────────┘
  ↓ passes: correlation_results
┌─────────────────────────────────────┐
│  STEP 3: RCA Generation             │
│  Agent: RCAGeneratorAgent           │
│  Type: LLM + RAG (ELSER)            │
│  LLM: Claude Sonnet 4               │
│  Time: ~1.5 minutes                 │
└─────────────────────────────────────┘
  ↓ passes: rca_analysis
┌─────────────────────────────────────┐
│  STEP 4: PIR Generation             │
│  Agent: PIRGeneratorAgent           │
│  Type: LLM-based                    │
│  LLM: Claude Sonnet 4               │
│  Time: ~1 minute                    │
└─────────────────────────────────────┘
  ↓
Output: Complete RCA + PIR document
Total time: ~5-6 minutes
```

---

## 📋 Implementation Checklist

### ✅ Phase 1 (COMPLETED)
- [x] Agent 1: Data Retriever (tool-based)
- [x] Workflow definition (YAML)
- [x] Test script
- [x] Documentation

### ⏳ Phase 2 (NEXT - 3-4 hours)
- [ ] Agent 2: Correlation Agent (LLM + tools)
  - Temporal pattern analysis
  - Claude Sonnet 4 reasoning
  - Statistical tools

### ⏳ Phase 3 (4-5 hours)
- [ ] Agent 3: RCA Generator (LLM + RAG)
  - 5 Whys methodology
  - ELSER semantic search
  - Evidence linking

### ⏳ Phase 4 (2-3 hours)
- [ ] Agent 4: PIR Generator (LLM-based)
  - Document formatting
  - Professional output

### ⏳ Phase 5 (2-3 hours)
- [ ] Workflow Runner
  - Orchestrates all agents
  - Manages data flow
  - Error handling

### ⏳ Phase 6 (2-3 hours)
- [ ] Testing & Polish
- [ ] Demo script
- [ ] Kibana dashboards

---

## 🎯 Agent 1 Output Structure

```json
{
  "incident": {
    "incident_id": "INC0012345",
    "app_id": "APP-2847",
    "severity": "P1",
    "created_at": "2026-02-04T09:00:00+11:00",
    "resolved_at": "2026-02-04T11:00:00+11:00",
    "description": "CustomerPortal API returning 500 errors...",
    "resolution_time_minutes": 120
  },
  "time_window": {
    "start": "2026-02-04T08:00:00+11:00",
    "end": "2026-02-04T11:00:00+11:00",
    "duration_hours": 2.0
  },
  "changes": [
    {
      "change_id": "CHG0089234",
      "app_id": "APP-2847",
      "implemented_at": "2026-02-04T08:00:00+11:00",
      "description": "Deploy v2.3.1 - traffic optimization"
    },
    {
      "change_id": "CHG0089235",
      "app_id": "APP-2847",
      "implemented_at": "2026-02-04T10:30:00+11:00",
      "description": "Update connection pool max size to 200"
    }
  ],
  "logs": {
    "application": [ /* 268 logs */ ],
    "infrastructure": [ /* 23 logs */ ]
  },
  "traces": [ /* 231 traces */ ],
  "communications": {
    "teams": [ /* 6 messages */ ],
    "emails": [ /* 2 emails */ ],
    "teams_count": 6,
    "email_count": 2
  },
  "metadata": {
    "total_documents": 533,
    "retrieval_time": "2026-02-04T13:55:00+11:00"
  }
}
```

This structured data feeds into Agent 2 (Correlation).

---

## 🔍 What Agent 2 Will Do (Next)

**Correlation Agent** will take Agent 1's output and:

1. **Temporal Analysis:**
   - Calculate time delta: Change → First Error
   - Identify error spike pattern
   - Determine correlation strength (0-1)

2. **LLM Reasoning:**
   - "Does the timing suggest causation?"
   - "What's the evidence strength?"
   - "Are there other contributing factors?"

3. **Output:**
   ```json
   {
     "temporal_correlation": {
       "change_to_first_error": "30 minutes",
       "error_rate_progression": [0, 5, 45, 38, 0],
       "correlation_strength": 0.95,
       "confidence": "HIGH"
     },
     "key_events": [
       {
         "time": "08:00",
         "event": "Deployment v2.3.1",
         "type": "change"
       },
       {
         "time": "08:30",
         "event": "First connection errors",
         "type": "error"
       }
     ]
   }
   ```

---

## 🚀 Next Steps

1. **Test Agent 1 now** - Verify it works with your data
2. **Tell me the output** - Confirm it retrieves all 533 documents
3. **I'll build Agent 2** - Correlation with LLM reasoning
4. **Then Agent 3 & 4** - Complete the workflow

We're building this step-by-step so you can test each component!

---

## ⏰ Timeline

- **Now:** Test Agent 1 ✅
- **Tonight (4 hours):** Build Agents 2, 3, 4
- **Tomorrow:** Workflow runner + testing
- **Feb 6-10:** Polish + dashboards
- **Feb 11:** 🎯 DEMO

---

**Run Agent 1 now and show me what you get!** 🚀
