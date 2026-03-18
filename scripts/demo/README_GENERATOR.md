# Continuous Memory Leak Data Generator

**Purpose:** Generate realistic time-series JVM memory metrics for live demo of alert-driven RCA automation.

---

## 📋 **What It Does**

- ✅ Generates 1 metric every 60 seconds (configurable)
- ✅ Simulates gradual memory leak (heap grows from 70% → 95%)
- ✅ Triggers alerts naturally when heap > 85%
- ✅ Runs in background with logging
- ✅ Graceful shutdown on Ctrl+C
- ✅ Saves state for resume capability

---

## 🚀 **Quick Start**

### **Setup (One-Time)**

```bash
# Navigate to demo directory
cd /path/to/elastic-agentic-rca-demo/scripts/demo

# Make scripts executable
chmod +x start_generator.sh stop_generator.sh

# Verify configuration
cat generator_config.json
```

### **Start Generator**

```bash
./start_generator.sh
```

**Output:**
```
==========================================
STARTING CONTINUOUS DATA GENERATOR
==========================================

🚀 Starting generator...
✅ Generator started successfully!
   PID: 12345

📊 Monitor with:
   tail -f generator.log

⏹️  Stop with:
   ./stop_generator.sh
==========================================
```

### **Monitor Progress**

```bash
# Watch logs in real-time
tail -f generator.log

# Check status
ps aux | grep continuous_memory_leak_generator
```

### **Stop Generator**

```bash
./stop_generator.sh
```

---

## ⚙️ **Configuration**

Edit `generator_config.json`:

```json
{
  "interval_seconds": 60,           // Time between metrics (60 = 1 min)
  "heap_start_percent": 70.0,       // Starting heap (70% = normal)
  "heap_increase_per_cycle": 2.5,   // Growth rate (2.5% per cycle)
  "heap_max_percent": 95.0,         // Max before restart (95% = OOM)
  "alert_threshold": 85.0,          // Alert fires above this
  "reset_after_max": true,          // Auto-restart at max
  "add_random_noise": true,         // Realistic fluctuations
  "noise_range": 1.5                // +/- fluctuation range
}
```

### **Pre-Configured Scenarios**

**Quick Demo (3 minutes to alert):**
```json
{
  "interval_seconds": 30,
  "heap_start_percent": 78.0,
  "heap_increase_per_cycle": 3.0
}
```

**Slow Burn (10 minutes to alert):**
```json
{
  "interval_seconds": 60,
  "heap_start_percent": 70.0,
  "heap_increase_per_cycle": 1.5
}
```

**Immediate Critical (fires now):**
```json
{
  "interval_seconds": 60,
  "heap_start_percent": 88.0,
  "heap_increase_per_cycle": 1.0
}
```

---

## 🎬 **Demo Day Usage (Feb 11, 2026)**

### **Option A: Start Before Demo (Recommended)**

**10 minutes before demo:**
```bash
# Start generator with quick demo config
./start_generator.sh

# Monitor until heap reaches ~82%
tail -f generator.log

# Stop when ready
./stop_generator.sh
```

**During demo:**
- Show Discover with recent metrics
- Point out growing heap trend
- Wait for alert to fire naturally
- Show workflow auto-execution

---

### **Option B: Live Generation During Demo**

**During demo:**
```bash
# Start generator
./start_generator.sh

# Open terminal window showing logs
tail -f generator.log
```

**Demo narrative:**
> "Our monitoring system runs continuously. Watch these metrics coming in real-time..."
> 
> [Show log output with heap percentages]
> 
> "See how heap usage is climbing? 82%... 84%... 86%..."
> 
> [Alert fires]
> 
> "There! The alert just fired automatically at 87%..."
> 
> [Show workflow execution]

---

## 📊 **Monitoring & Verification**

### **Check Metrics in Kibana**

**Discover search:**
```
app_id:"APP-9123" AND metric_type:"jvm.memory.heap" AND generated_by:"continuous_generator"
```

**Time range:** Last 15 minutes

**Expected:** New metrics appearing every 60 seconds

### **Check Alert Status**

**Go to:** Stack Management → Rules → "JVM Heap Memory Critical - PaymentService"

**Expected:** 
- Alert fires when heap > 85%
- Workflow triggered automatically

### **Check Workflow Executions**

**Go to:** Workflows → "Alert-Driven RCA - Memory Leak" → Executions

**Expected:** 
- New execution triggered by alert
- Status: SUCCESS
- All 6 steps completed

---

## 🐛 **Troubleshooting**

### **Generator won't start**

```bash
# Check if already running
ps aux | grep continuous_memory_leak_generator

# Check logs
cat generator.log

# Verify Elasticsearch connection
python -c "from scripts.utilities.es_client import get_es_client; print(get_es_client().info())"
```

### **No metrics appearing**

```bash
# Check generator is running
cat generator.pid
ps -p $(cat generator.pid)

# Check logs for errors
tail -n 50 generator.log

# Verify ES connection
curl -X GET "localhost:9200/rca-metrics/_count?q=app_id:APP-9123"
```

### **Alert not firing**

```bash
# Check recent metrics
# In Kibana Dev Tools:
GET rca-metrics/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"app_id": "APP-9123"}},
        {"range": {"heap_percent": {"gte": 85}}}
      ]
    }
  },
  "sort": [{"@timestamp": "desc"}],
  "size": 1
}

# Verify alert rule is enabled
# Stack Management → Rules → Check "JVM Heap Memory Critical"
```

---

## 📁 **Files Created**

```
scripts/demo/
├── continuous_memory_leak_generator.py   # Main generator
├── generator_config.json                 # Configuration
├── start_generator.sh                    # Start script
├── stop_generator.sh                     # Stop script
├── generator.log                         # Output log (created on run)
├── generator.pid                         # Process ID (created on run)
├── generator_state.json                  # State file (created on run)
└── README.md                             # This file
```

---

## 🎯 **Key Features**

### **Realistic Simulation**
- Progressive memory leak pattern
- Random noise for realism
- Simulates service restarts at max heap

### **Demo-Friendly**
- Visual progress bars in logs
- Alert status indicators
- Configurable timing for demo control

### **Production-Ready**
- Graceful shutdown (Ctrl+C)
- State persistence (resume capability)
- Error handling and retries
- Background execution with logging

---

## 🏆 **Expected Demo Flow**

```
T+0:00  Start generator (heap: 70%)
T+1:00  Metric 1 generated (heap: 72.5%)
T+2:00  Metric 2 generated (heap: 75%)
T+3:00  Metric 3 generated (heap: 77.5%)
T+4:00  Metric 4 generated (heap: 80%)
T+5:00  Metric 5 generated (heap: 82.5%)
T+6:00  Metric 6 generated (heap: 85%) ← Alert fires!
T+6:30  Workflow triggered automatically
T+9:30  Workflow completes (3 min execution)
        → Incident created
        → Team notified
        → Knowledge base updated
```

**Total demo time: 10 minutes of autonomous automation!** 🎉

---

## ✅ **Demo Checklist**

**Before Demo:**
- [ ] Test generator (start, monitor, stop)
- [ ] Verify alert fires at 85%
- [ ] Verify workflow triggers automatically
- [ ] Practice demo narrative
- [ ] Have backup plan (manual data injection)

**Day Before Demo:**
- [ ] Stop any running generators
- [ ] Clear old metrics: `DELETE /rca-metrics/_query?q=generated_by:continuous_generator`
- [ ] Test full flow one more time
- [ ] Charge laptop, stable internet

**Demo Day:**
- [ ] Start generator 5-10 min before demo
- [ ] Open monitoring terminal
- [ ] Have Kibana tabs ready
- [ ] Confidence level: 💯

---

## 🚀 **You're Ready!**

This generator proves **complete autonomous RCA automation** from alert detection to incident resolution!

**Feb 11, 2026 @ 2:00 PM - Let's show them what AgenticAI can do!** 💪
