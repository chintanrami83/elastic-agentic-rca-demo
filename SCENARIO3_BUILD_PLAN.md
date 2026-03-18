# Scenario 3 — Distributed System RCA Reference

Scenario 3 demonstrates AI-driven root cause analysis of a cascading failure across 3 microservices — the type of incident that is hardest for humans to debug manually.

---

## Incident Summary

| Field | Value |
|---|---|
| Incident ID | `INC0034567` |
| Date | Feb 3, 2026, 14:00–16:15 AEDT |
| Type | Cascading timeout |
| Services affected | 3 |
| Documents analyzed | 228+ |
| AI analysis time | ~3 minutes |

---

## Service Chain

```
Customer Request
      ↓
OrderProcessing Gateway (APP-7654)  ← Symptoms visible here
      ↓
InventoryService (APP-5521)         ← Timeouts
      ↓
PaymentService (APP-9123)           ← Slowness
      ↓
Stripe API                          ← ROOT CAUSE
```

Symptoms appear in `OrderProcessing`. Root cause is `Stripe API` degradation 3 layers downstream.

---

## Failure Timeline

| Time | Event |
|---|---|
| 14:00 | Stripe API response times begin increasing |
| 14:03 | PaymentService (APP-9123) response time spikes: 500ms → 4,000ms |
| 14:05 | InventoryService (APP-5521) begins timing out waiting for Payment |
| 14:08 | OrderProcessing Gateway (APP-7654) error rate spikes to 45% |
| 14:15 | Alert fires on OrderProcessing error rate |
| 16:15 | Incident resolved after switching to backup payment gateway |

---

## Data Ingested

| Source | Count | Index |
|---|---|---|
| Incident record | 1 | `incidents-servicenow` |
| Application logs (3 services) | 28 | `logs-application` |
| Metrics (3 services) | 135 | `rca-metrics` |
| Distributed traces | 27 | `traces-apm` |
| Teams messages | 5 | `comms-teams` |
| Alerts | 2 | `rca-alerts` |
| KB article | 1 | `knowledge-base` |

---

## Kibana Verification Queries

**All scenario 3 data:**
```
incident_id:"INC0034567"
```
Time range: Feb 3, 2026 13:30–17:00

**PaymentService metrics (root cause service):**
```
app_id:"APP-9123"
```

**InventoryService (first to show timeouts):**
```
app_id:"APP-5521"
```

**OrderProcessing Gateway (where symptoms appear):**
```
app_id:"APP-7654"
```

**Distributed traces (shows full service chain):**
```
_index:"traces-apm"
```

---

## What the rca_agent Does

When triggered with `incident_id: INC0034567`, the agent uses the `distributed_system_analyzer` ES|QL tool to:

1. Retrieve data across all 3 services simultaneously
2. Build a service dependency map from the distributed traces
3. Identify temporal sequence — which service degraded first
4. Trace backwards from OrderProcessing → Inventory → Payment → Stripe
5. Identify Stripe API as the external root cause
6. Generate a PIR with 5 Whys, impact assessment, and prevention recommendations (circuit breakers, backup gateways)

---

## Running This Scenario

### Manual trigger via Elastic Workflow:
1. Go to **Kibana → Workflows**
2. Select the Distributed System RCA workflow
3. Input: `incident_id = INC0034567`
4. Run and observe agent output

### Expected output includes:
- Service dependency map
- Temporal cascade timeline
- Root cause: Stripe API degradation
- Evidence from distributed traces
- Preventive measures: circuit breakers, fallback payment gateway
