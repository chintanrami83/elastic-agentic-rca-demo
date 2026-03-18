# Continuous Memory Leak Data Generator

Generates live JVM heap metrics into Elasticsearch to trigger the Kibana alert for Scenario 2 (Alert-Driven RCA).

---

## What It Does

- Writes one JVM heap metric every 60 seconds to `rca-metrics`
- Simulates a gradual memory leak: heap grows from ~70% → 95%
- When heap exceeds 85%, your Kibana alert fires automatically
- The Elastic Workflow then triggers `rca_agent` with zero human intervention

---

## Quick Start

```bash
# From the repo root
bash scripts/demo/start_generator.sh

# Monitor progress
tail -f scripts/demo/generator.log

# Stop when done
bash scripts/demo/stop_generator.sh
```

---

## Configuration

Edit `scripts/demo/generator_config.json`:

```json
{
  "interval_seconds": 60,
  "heap_start_percent": 70.0,
  "heap_increase_per_cycle": 2.5,
  "heap_max_percent": 95.0,
  "alert_threshold": 85.0,
  "reset_after_max": true,
  "add_random_noise": true,
  "noise_range": 1.5
}
```

**Pre-configured profiles:**

| Profile | Change | Time to alert |
|---|---|---|
| Default | `interval: 60, increase: 2.5` | ~6 minutes |
| Quick | `interval: 30, increase: 3.0, start: 78` | ~3 minutes |
| Immediate | `start: 88, increase: 1.0` | ~1 minute |

---

## Verifying in Kibana

**Check metrics are flowing:**
```
app_id:"APP-9123" AND metric_type:"jvm.memory.heap"
```
Time range: Last 15 minutes. New docs should appear every 60 seconds.

**Check alert status:**
Kibana → Stack Management → Rules → "JVM Heap Memory Critical - PaymentService"

**Check workflow triggered:**
Kibana → Workflows → Executions

---

## Troubleshooting

**Generator won't start:**
```bash
# Check if already running
cat scripts/demo/generator.pid
ps -p $(cat scripts/demo/generator.pid)

# Check logs
tail -n 50 scripts/demo/generator.log
```

**Alert not firing:**
Verify the Kibana alerting rule exists and is enabled.
Check that `heap_percent` values above 85 exist in `rca-metrics`:
```
app_id:"APP-9123" AND heap_percent:>85
```

**No metrics in Kibana:**
Confirm Elasticsearch connectivity:
```bash
python scripts/utilities/test_connectivity.py
```
