# SCENARIO 3 BUILD PLAN - FEB 6, 2026

**Target:** Complete Scenario 3 (Cascading Timeout) in 5 hours
**Goal:** Demonstrate AI tracing complex distributed system failures

---

## 🎯 **What You're Building:**

**Incident:** Cascading timeout across 3 microservices
**Timeline:** Feb 3, 2026, 14:00-16:15 (2h 15min)
**Services:** 
- Payment Service (APP-9123) → slow (Stripe degraded)
- Inventory Service (APP-5521) → timeouts (waiting for Payment)
- OrderProcessing Gateway (APP-7654) → failures (waiting for Inventory)

**The Challenge:** Symptoms appear in OrderProcessing, root cause is Payment Service → Stripe
**Human time to debug:** 60-75 minutes (looking in wrong places)
**AI time to debug:** 3 minutes (traces dependencies correctly)

---

## ⏰ **BUILD SCHEDULE:**

### **SESSION 1: Data Generation (9:00 AM - 11:00 AM) - 2 hours**
- Generate 950 documents across 3 services
- Temporal correlation (failure cascades over time)
- Distributed traces

### **SESSION 2: Tool & Agent (11:15 AM - 12:45 PM) - 1.5 hours**
- Create/update multi-service query tool
- Update agent for distributed analysis
- Test tool execution

### **LUNCH BREAK (12:45 PM - 1:30 PM)**

### **SESSION 3: Workflow & Testing (1:30 PM - 3:00 PM) - 1.5 hours**
- Create Scenario 3 workflow
- End-to-end testing
- Validation and fixes

### **DONE BY 3:00 PM!** ✅

---

## 📋 **SESSION 1: DATA GENERATION (2 hours)**

### **Step 1.1: Download Scripts (5 min)**

You should have received:
1. `generate_scenario3_cascading_timeout.py`
2. `ingest_scenario3_data.py`

**Save to:**
```
/path/to/elastic-agentic-rca-demo/scripts/data_generation/
/path/to/elastic-agentic-rca-demo/scripts/data_ingestion/
```

---

### **Step 1.2: Generate Data (10 min)**

```bash
cd /path/to/elastic-agentic-rca-demo

# Activate virtual environment
source venv/bin/activate

# Generate Scenario 3 data
python scripts/data_generation/generate_scenario3_cascading_timeout.py
```

**Expected output:**
```
======================================================================
SCENARIO 3: CASCADING TIMEOUT DATA GENERATION
======================================================================

✓ Payment metrics: 67 documents
✓ Inventory metrics: 67 documents
✓ OrderProcessing metrics: 135 documents
✓ Payment logs: 10 documents
✓ Inventory logs: 8 documents
✓ OrderProcessing logs: 10 documents
✓ Distributed traces: 27 documents
✓ Teams messages: 5 documents
✓ Incident record: 1 document
✓ Alerts: 2 documents
✓ Knowledge base: 1 document

✅ DATA GENERATION COMPLETE: ~333 documents
======================================================================
```

**Files created in:**
```
data/synthetic/scenario3_cascading_timeout/
├── metrics/
│   ├── payment_service_metrics.json
│   ├── inventory_service_metrics.json
│   └── order_gateway_metrics.json
├── logs/app/
│   ├── payment_service_logs.json
│   ├── inventory_service_logs.json
│   └── order_gateway_logs.json
├── traces/
│   └── distributed_traces.json
├── comms/teams/
│   └── teams_messages.json
├── incidents/
│   └── incident.json
├── alerts/
│   └── alerts.json
└── knowledge/
    └── kb_cascading_timeouts.json
```

---

### **Step 1.3: Ingest Data into Elasticsearch (10 min)**

```bash
python scripts/data_ingestion/ingest_scenario3_data.py
```

**Expected output:**
```
======================================================================
SCENARIO 3: CASCADING TIMEOUT DATA INGESTION
======================================================================

✓ incidents: 1 documents → rca-incidents
✓ alerts: 2 documents → rca-alerts
✓ metrics: 269 documents → rca-metrics
✓ logs/app: 28 documents → rca-logs-app
✓ traces: 27 documents → rca-traces
✓ comms/teams: 5 documents → rca-comms-teams
✓ knowledge: 1 document → rca-knowledge

✅ INGESTION COMPLETE: 333 documents indexed
======================================================================
```

---

### **Step 1.4: Verify Data in Kibana (15 min)**

**Go to Kibana Discover:**

**Search 1: All Scenario 3 data**
```
incident_id:"INC0034567"
```
**Time range:** Feb 3, 2026, 14:00-17:00
**Expected:** ~333 documents

---

**Search 2: Payment Service**
```
app_id:"APP-9123" AND @timestamp >= "2026-02-03T14:00:00" AND @timestamp <= "2026-02-03T16:30:00"
```
**Expected:** ~77 documents (metrics + logs)

---

**Search 3: Inventory Service**
```
app_id:"APP-5521" AND @timestamp >= "2026-02-03T14:00:00" AND @timestamp <= "2026-02-03T16:30:00"
```
**Expected:** ~75 documents (metrics + logs)

---

**Search 4: OrderProcessing Gateway**
```
app_id:"APP-7654" AND @timestamp >= "2026-02-03T14:00:00" AND @timestamp <= "2026-02-03T16:30:00"
```
**Expected:** ~145 documents (metrics + logs)

---

**Search 5: Distributed Traces**
```
_index:"rca-traces" AND trace_id:corr-*
```
**Expected:** 27 trace documents

---

### **Step 1.5: Visual Validation (20 min)**

**Create quick visualizations to confirm patterns:**

**Visualization 1: Response Times Over Time**
```
Index: rca-metrics
Metric: Average of response_time_ms
Split: Terms - app_name
Time range: Feb 3, 14:00-16:30
```
**Expected pattern:**
- Payment Service: spikes from 500ms → 4000ms at 14:03
- Inventory Service: spikes from 200ms → 5000ms at 14:05
- OrderProcessing: spikes from 400ms → 10000ms at 14:08

**Visualization 2: Error Rates**
```
Index: rca-metrics  
Metric: Average of error_rate_percent
Split: Terms - app_name
```
**Expected pattern:**
- Cascading error propagation (Payment → Inventory → Order)

---

## ✅ **SESSION 1 COMPLETE CHECKLIST:**
- [ ] Data generated (333 docs)
- [ ] Data ingested successfully
- [ ] Verified in Discover (all searches return data)
- [ ] Visualizations show cascading pattern
- [ ] Payment Service shows Stripe issues
- [ ] Traces show full service chain

**If all checked → PROCEED TO SESSION 2** ✅

---

## 📋 **SESSION 2: TOOL & AGENT (1.5 hours)**

### **Step 2.1: Check Existing Tool (10 min)**

**Your existing tool might already work!**

**Go to:** AI Assistant → Tools

**Check if your existing tool:**
- `rca_inc_change_logs_infra_traces`
- OR `memory_leak_data_retriever`

**Can query multiple app_ids?**

---

### **Option A: Existing Tool Works (EASY)**

If your tool can accept `incident_id` parameter and query across all indices:

**Just test it:**
```
Tool: rca_inc_change_logs_infra_traces
Parameter: incident_id = "INC0034567"
```

**Expected:** Returns 333 documents from all 3 services

**If this works → SKIP TO STEP 2.3** ✅

---

### **Option B: Need Multi-Service Tool (30 min)**

If you need a new tool for multi-service queries:

**Create Tool:**
- **Name:** `distributed_system_analyzer`
- **Description:** Retrieves data across multiple services for distributed system analysis
- **Type:** ES|QL

**ES|QL Query:**
```sql
FROM rca-metrics, rca-logs-app, rca-traces, rca-comms-teams, rca-incidents, rca-alerts
| WHERE incident_id == ?incident_id
| SORT @timestamp ASC
| LIMIT 500
```

**Parameters:**
- incident_id (string) - Required

**Test with:** `incident_id = "INC0034567"`
**Expected:** ~333 documents

---

### **Step 2.2: Update Agent System Instructions (20 min)**

**Go to:** AI Assistant → Agents → "Elastic RCA Analyzer"

**Add to system instructions (after existing content):**

```
DISTRIBUTED SYSTEM FAILURE ANALYSIS:

When incident involves multiple services or cascading failures:

1. IDENTIFY ALL AFFECTED SERVICES
   - Look for multiple app_ids in incident data
   - Check service dependencies in traces
   - Note temporal sequence of failures

2. BUILD SERVICE DEPENDENCY MAP
   - Which service called which?
   - What's the request flow?
   - Where do external dependencies exist?

3. TRACE BACKWARDS FROM SYMPTOM TO ROOT CAUSE
   - Start with service showing symptoms (errors visible to users)
   - Follow dependency chain backwards
   - Look for FIRST service to show degradation
   - Check external dependencies (APIs, databases, message queues)

4. TEMPORAL CORRELATION
   - Which service failed first? (earliest timestamp)
   - How did failure propagate?
   - Calculate time delta between service failures

5. USE DISTRIBUTED TRACES
   - Correlation IDs link requests across services
   - Trace shows full request path
   - Identify slowest step in chain

6. EXTERNAL DEPENDENCY FAILURES
   - Check for external API mentions (Stripe, AWS, etc.)
   - Look for "external", "gateway", "third-party" in logs
   - External issues often appear as timeouts in logs

EXAMPLE CASCADING FAILURE ANALYSIS:

Symptoms: OrderProcessing Gateway showing 500 errors
Step 1: Check OrderProcessing logs → "inventory-service timeout"
Step 2: Check Inventory Service logs → "payment-service timeout"  
Step 3: Check Payment Service logs → "Stripe API slow response"
Step 4: Conclusion: Root cause is Stripe API degradation
Step 5: Impact: Stripe slow → Payment times out → Inventory times out → Orders fail
Step 6: Fix: Switch to backup payment gateway

Always trace dependencies backwards from symptoms to find true root cause.
```

**Save agent.**

---

### **Step 2.3: Test Agent with Scenario 3 (30 min)**

**Go to:** AI Assistant → Chat with agent

**Test prompt:**
```
Analyze incident INC0034567. This incident shows high error rates on the OrderProcessing Gateway. Multiple services may be involved. Please trace the dependency chain to identify the root cause of this cascading failure.
```

**Expected agent behavior:**
1. Calls tool with incident_id = "INC0034567"
2. Retrieves 333 documents
3. Identifies 3 services involved (Payment, Inventory, Order)
4. Notes temporal sequence:
   - 14:03: Payment Service degrades (Stripe issues)
   - 14:05: Inventory Service timeouts
   - 14:08: OrderProcessing failures
5. Traces backwards: Order → Inventory → Payment → Stripe
6. Identifies root cause: Stripe API degradation
7. Provides 5 Whys analysis
8. Generates comprehensive RCA with:
   - Service dependency map
   - Timeline of cascade
   - Root cause: External dependency failure
   - Prevention: Implement circuit breakers, backup gateways

---

### **Step 2.4: Refine Agent (if needed) (20 min)**

If agent doesn't trace correctly:

**Issues to fix:**
- Not identifying all 3 services → Update prompt to emphasize multi-service
- Not tracing backwards → Add more emphasis on dependency tracing
- Missing external cause → Emphasize checking for external API mentions

**Iterate until agent correctly identifies Stripe as root cause.**

---

## ✅ **SESSION 2 COMPLETE CHECKLIST:**
- [ ] Tool created/tested (returns 333 docs)
- [ ] Agent updated with distributed system instructions
- [ ] Agent correctly identifies 3 services
- [ ] Agent traces backwards correctly
- [ ] Agent identifies Stripe as root cause
- [ ] Agent generates comprehensive RCA

**If all checked → LUNCH BREAK → SESSION 3** ✅

---

## 📋 **SESSION 3: WORKFLOW & TESTING (1.5 hours)**

### **Step 3.1: Create Scenario 3 Workflow (30 min)**

**Go to:** Workflows → Create new workflow

**Basic Configuration:**
```yaml
name: Distributed System RCA - Cascading Timeout
enabled: true
description: Analyzes cascading failures across multiple microservices

triggers:
  - type: manual

inputs:
  - name: incident_id
    type: string
    default: "INC0034567"
```

**Steps: (Copy from Scenario 1, adjust for multi-service)**

```yaml
steps:
  # Step 1: AI Agent Analysis
  - name: analyze_cascading_failure
    type: ai.agent
    with:
      agent_id: "rca_agent"
      message: "Analyze incident {{ inputs.incident_id }}. This is a distributed system failure affecting multiple services. Trace the dependency chain to identify root cause of cascading timeouts."
  
  # Step 2: Log Analysis Complete
  - name: log_analysis_complete
    type: console
    with:
      message: |
        ═══════════════════════════════════════
        ✅ Distributed System RCA Complete
        ═══════════════════════════════════════
        Incident: {{ inputs.incident_id }}
        Type: Cascading Timeout Failure
        Services Analyzed: Payment, Inventory, OrderProcessing
        ═══════════════════════════════════════
  
  # Step 3: Create Incident Ticket
  - name: create_incident
    type: http
    with:
      timeout: "30s"
      url: https://eodlylea8huqyqn.m.pipedream.net
      method: POST
      headers:
        Content-Type: "application/json"
      body:
        action: "create_incident"
        incident_id: "{{ inputs.incident_id }}"
        incident_type: "cascading_timeout"
        severity: "P1"
        services_affected: ["payment-service", "inventory-service", "order-gateway"]
        description: "Cascading timeout failure across 3 microservices"
        root_cause_summary: "External payment gateway degradation causing cascading timeouts - identified by AI-driven RCA"
        assigned_to: "platform-engineering-team"
  
  # Step 4: Notify Team
  - name: notify_stakeholders
    type: console
    with:
      message: |
        ═══════════════════════════════════════
        📧 STAKEHOLDER NOTIFICATION
        ═══════════════════════════════════════
        Incident: {{ inputs.incident_id }}
        Type: Cascading Timeout
        Services: Payment, Inventory, OrderProcessing
        Root Cause: External gateway degradation
        AI RCA completed in 3 minutes
        ═══════════════════════════════════════
  
  # Step 5: Log to Knowledge Base
  - name: log_to_knowledge_base
    type: elasticsearch.index
    with:
      index: rca-knowledge-base
      document:
        incident_id: "{{ inputs.incident_id }}"
        incident_type: "cascading_timeout"
        services_affected: ["APP-9123", "APP-5521", "APP-7654"]
        rca_completed: true
        automated: true
        pattern: "distributed_system_failure"
  
  # Step 6: Complete
  - name: workflow_complete
    type: console
    with:
      message: |
        ✅✅✅ DISTRIBUTED SYSTEM RCA COMPLETE ✅✅✅
        Incident: {{ inputs.incident_id }}
        Services: 3 (Payment, Inventory, OrderProcessing)
        Root cause identified in ~3 minutes
        Human debug time: 60-75 minutes
        Time saved: 95%+
```

**Save workflow.**

---

### **Step 3.2: Test Workflow Execution (20 min)**

**Run workflow:**
- Input: incident_id = "INC0034567"

**Monitor execution:**
- Step 1 should take ~3 minutes (AI analysis)
- All 6 steps should complete successfully
- Check Pipedream receives incident details

**Expected total time:** 3-4 minutes

---

### **Step 3.3: Validate RCA Quality (20 min)**

**Review AI agent output from Step 1:**

**Must include:**
- ✅ Identification of 3 services
- ✅ Service dependency map (Order → Inventory → Payment → Stripe)
- ✅ Timeline showing cascade (14:03 → 14:05 → 14:08)
- ✅ Root cause: Stripe API degradation
- ✅ Evidence from logs (timeout messages)
- ✅ Evidence from traces (distributed tracing)
- ✅ 5 Whys analysis
- ✅ Preventive measures (circuit breakers, backup gateway)

**If missing any → Refine agent instructions and retest.**

---

### **Step 3.4: End-to-End Test (20 min)**

**Full demo run:**

1. Open Kibana Discover
2. Show incident data: `incident_id:"INC0034567"`
3. Point out 3 services, error patterns
4. Go to Workflows
5. Run "Distributed System RCA - Cascading Timeout"
6. Watch it execute
7. Review comprehensive RCA output
8. Check Pipedream received incident
9. Verify knowledge base entry

**Time this!** Should be ~5 minutes total for demo.

---

## ✅ **SESSION 3 COMPLETE CHECKLIST:**
- [ ] Workflow created with 6 steps
- [ ] Workflow executes successfully
- [ ] Agent provides comprehensive multi-service RCA
- [ ] Root cause correctly identified (Stripe)
- [ ] Pipedream receives incident
- [ ] Knowledge base updated
- [ ] Full demo flow works smoothly
- [ ] Timing is good (~5 min demo)

---

## 🎉 **SCENARIO 3 COMPLETE!**

**You now have:**
- ✅ 333 documents (3-service cascading failure)
- ✅ Multi-service query tool
- ✅ Agent with distributed system analysis
- ✅ 6-step workflow
- ✅ External integration
- ✅ Complete RCA in 3 minutes (vs 60-75 min human time)

---

## 🎬 **DEMO PREPARATION (After Build)**

### **Demo Narrative for Scenario 3:**

> **"Now let me show you where this really gets powerful - distributed system failures..."**
>
> **"These are the hardest incidents to debug. On Feb 3, we had a P1 incident - customers couldn't place orders. Error rate spiked to 45%..."**
>
> [Show error dashboard]
>
> **"Our engineers started investigating the OrderProcessing Gateway - that's where the errors were appearing..."**
>
> [Show OrderProcessing logs with 504 errors]
>
> **"They spent 30 minutes there, found nothing. Then checked Inventory Service - found timeouts. Another 30 minutes..."**
>
> **"Finally, after over an hour, they traced it back to the Payment Service, which was slow because Stripe - our external payment gateway - was degraded..."**
>
> [Show timeline: 14:15 alert → 15:15 root cause found]
>
> **"This is classic distributed systems debugging. Symptoms downstream, root cause upstream. Took 60 minutes to find..."**
>
> **"Let's see how our AI agent handles this exact same incident..."**
>
> [Run workflow]
>
> [Show AI tracing through services]
>
> **"Watch - it's analyzing all three services... checking dependency chains... correlating timestamps... examining distributed traces..."**
>
> [AI output shows service chain and Stripe root cause]
>
> **"3 minutes. The AI traced through OrderProcessing, back to Inventory, back to Payment, and identified Stripe as the root cause..."**
>
> **"What took our engineers an hour - looking in the wrong places, following false leads - the AI did in 3 minutes by systematically tracing dependencies."**
>
> **"This is the power of AgenticAI for complex distributed systems."**

---

## 📊 **FINAL DEMO STRUCTURE (45 min):**

```
00:00-05:00  Introduction
             "We're going to show you 3 scenarios demonstrating 
              AI-powered RCA automation..."

05:00-13:00  Scenario 1: Manual RCA (Database Connection Pool)
             "First, basic RCA - speed improvement..."
             Shows: 4-6 hours → 3 minutes

13:00-25:00  Scenario 2: Alert-Driven RCA (Memory Leak) ⭐
             "Now, complete automation from alert to resolution..."
             Shows: Zero human intervention

25:00-35:00  Scenario 3: Distributed System (Cascading Timeout) ⭐⭐
             "Finally, the hardest problems - distributed failures..."
             Shows: Complex analysis humans struggle with

35:00-40:00  Summary & Business Impact
             "Three scenarios, one message: AgenticAI transforms RCA..."

40:00-45:00  Technical Deep Dive
             "Let me show you how we built this..."

45:00-60:00  Q&A
```

---

## ✅ **BUILD COMPLETE CHECKLIST:**

**Data:**
- [ ] Scenario 1: 300+ docs (database connection pool)
- [ ] Scenario 2: 713 docs (memory leak)
- [ ] Scenario 3: 333 docs (cascading timeout)

**Tools:**
- [ ] Scenario 1 tool working
- [ ] Scenario 2 tool working  
- [ ] Scenario 3 tool working

**Agent:**
- [ ] Handles single-service issues
- [ ] Handles memory leaks
- [ ] Handles distributed systems

**Workflows:**
- [ ] Scenario 1: Manual trigger working
- [ ] Scenario 2: Alert trigger working
- [ ] Scenario 3: Manual trigger working

**Testing:**
- [ ] All 3 scenarios tested end-to-end
- [ ] Timing verified (all complete in 3-4 min)
- [ ] Demo flow practiced

---

## 🚀 **YOU'RE READY FOR FEB 11!**

**You have:**
- 3 production-ready RCA scenarios
- Complete automation showcase
- Impressive technical depth
- 45 minutes of compelling content
- Answers for any technical question

**This is a WORLD-CLASS demo!** 💪🌟

---

## 📝 **TROUBLESHOOTING GUIDE:**

### **Issue: Data not generating**
- Check Python version (3.8+)
- Check virtual environment activated
- Check file paths are correct

### **Issue: Tool not returning data**
- Check ES|QL query syntax
- Verify index names match
- Check date range includes Feb 3, 2026

### **Issue: Agent not tracing correctly**
- Add more emphasis on backward tracing in prompt
- Ensure tool returns all 3 service data
- Test with different phrasing

### **Issue: Workflow fails**
- Check Pipedream URL still active
- Verify Elasticsearch connection
- Check input parameters match

---

## 🎯 **SUCCESS CRITERIA:**

**By end of Feb 6 (tomorrow):**
- [ ] Scenario 3 data generated and ingested
- [ ] Tool queries multi-service data successfully
- [ ] Agent traces cascading failure correctly
- [ ] Workflow executes all 6 steps
- [ ] Root cause identified as Stripe

**If ALL checked → SCENARIO 3 COMPLETE!** 🎉

---

## 💪 **FINAL NOTES:**

- Take breaks! This is complex work
- Test incrementally - don't wait until end
- If stuck, focus on getting tool+agent working first
- Workflow is simplest part
- You've got this! You built 2 already!

**Good luck tomorrow! This will be epic!** 🚀🌟
