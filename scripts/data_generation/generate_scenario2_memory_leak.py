"""
Scenario 2: Alert-Driven Memory Leak RCA
Generates realistic time-series data showing progressive JVM heap exhaustion

Timeline: Feb 4, 2026 (Yesterday) - 08:00 AM to 01:15 PM
Pattern: Progressive heap growth from deployment to OOM crash
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent if Path(__file__).parent.parent.parent.exists() else Path.cwd()
DATA_DIR = BASE_DIR / "data" / "synthetic" / "scenario2_memory_leak"

# Scenario details
APP_ID = "APP-9123"
APP_NAME = "PaymentService API"
INCIDENT_ID = "INC0023456"
CHANGE_ID = "CHG0098765"
DEPLOYMENT_VERSION = "v3.1.0"

# Timeline (Feb 4, 2026 - Yesterday)
START_TIME = datetime(2026, 2, 4, 8, 0, 0)  # 08:00 AM
DEPLOYMENT_TIME = START_TIME
ALERT_TIME = START_TIME + timedelta(hours=4, minutes=30)  # 12:30 PM
CRASH_TIME = START_TIME + timedelta(hours=5)  # 13:00 PM
RESOLUTION_TIME = START_TIME + timedelta(hours=5, minutes=15)  # 13:15 PM

# Heap parameters
HEAP_MAX_MB = 4096  # 4GB max heap
HEAP_INITIAL = 40  # Start at 40%


def calculate_heap_percent(minutes_since_start):
    """Calculate realistic heap percentage based on time progression"""
    hours = minutes_since_start / 60.0
    
    if hours < 1:
        return 40 + random.uniform(0, 10)
    elif hours < 2:
        progress = (hours - 1) / 1
        return 50 + (progress * 10) + random.uniform(-2, 2)
    elif hours < 3:
        progress = (hours - 2) / 1
        return 60 + (progress * 10) + random.uniform(-2, 2)
    elif hours < 4:
        progress = (hours - 3) / 1
        return 70 + (progress * 10) + random.uniform(-1, 1)
    elif hours < 4.5:
        progress = (hours - 4) / 0.5
        return 80 + (progress * 5) + random.uniform(-0.5, 0.5)
    elif hours < 5:
        progress = (hours - 4.5) / 0.5
        return 85 + (progress * 13) + random.uniform(-0.5, 1)
    else:
        return 98 + random.uniform(0, 2)


def ensure_directories():
    """Create all required directories"""
    dirs = [
        DATA_DIR / "incidents",
        DATA_DIR / "changes",
        DATA_DIR / "logs" / "app",
        DATA_DIR / "logs" / "infra",
        DATA_DIR / "metrics",
        DATA_DIR / "traces",
        DATA_DIR / "comms" / "teams",
        DATA_DIR / "comms" / "email",
        DATA_DIR / "knowledge",
        DATA_DIR / "alerts"
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def generate_change():
    """Generate deployment change record"""
    change = {
        "change_id": CHANGE_ID,
        "app_id": APP_ID,
        "app_name": APP_NAME,
        "change_type": "deployment",
        "version_from": "v3.0.4",
        "version_to": DEPLOYMENT_VERSION,
        "implemented_at": DEPLOYMENT_TIME.isoformat(),
        "implemented_by": "deployment-pipeline",
        "approval_status": "approved",
        "risk_level": "medium",
        "description": "Deploy v3.1.0 with new caching implementation for customer session data",
        "change_details": {
            "components_changed": ["SessionCacheManager", "PaymentContextCache", "UserPreferencesCache"],
            "files_modified": 23,
            "lines_added": 456,
            "lines_removed": 123
        },
        "rollback_plan": "Automated rollback to v3.0.4 via deployment pipeline",
        "testing_completed": True,
        "load_test_passed": True,
        "deployment_method": "blue-green",
        "environment": "production",
        "region": "ap-southeast-2"
    }
    
    filepath = DATA_DIR / "changes" / f"{CHANGE_ID}.json"
    with open(filepath, 'w') as f:
        json.dump(change, f, indent=2)
    
    return change


def generate_memory_metrics():
    """Generate 5 hours of memory metrics (every minute = 301 metrics)"""
    metrics = []
    total_minutes = 5 * 60 + 1
    
    for minute in range(total_minutes):
        timestamp = START_TIME + timedelta(minutes=minute)
        heap_percent = calculate_heap_percent(minute)
        heap_used_mb = int((heap_percent / 100) * HEAP_MAX_MB)
        
        metric = {
            "@timestamp": timestamp.isoformat(),
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "metric_type": "jvm.memory.heap",
            "heap_used_mb": heap_used_mb,
            "heap_max_mb": HEAP_MAX_MB,
            "heap_percent": round(heap_percent, 2),
            "old_gen_used_mb": int(heap_used_mb * 0.85),
            "young_gen_used_mb": int(heap_used_mb * 0.15),
            "non_heap_used_mb": random.randint(200, 300),
            "thread_count": random.randint(80, 120),
            "host": "payment-api-prod-03",
            "environment": "production"
        }
        
        metrics.append(metric)
    
    filepath = DATA_DIR / "metrics" / "jvm_heap_metrics.json"
    with open(filepath, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    return metrics


def generate_gc_logs():
    """Generate GC logs with increasing frequency"""
    gc_logs = []
    total_minutes = 5 * 60 + 1
    
    for minute in range(0, total_minutes, 2):  # Every 2 minutes
        timestamp = START_TIME + timedelta(minutes=minute)
        heap_percent = calculate_heap_percent(minute)
        
        # GC frequency increases with heap pressure
        if heap_percent < 60:
            gc_count = random.randint(1, 3)
        elif heap_percent < 75:
            gc_count = random.randint(3, 8)
        elif heap_percent < 85:
            gc_count = random.randint(8, 15)
        else:
            gc_count = random.randint(15, 30)
        
        gc_time = gc_count * random.randint(50, 200)
        
        log = {
            "@timestamp": timestamp.isoformat(),
            "app_id": APP_ID,
            "log_type": "gc",
            "gc_type": "Full GC" if heap_percent > 80 else "Young GC",
            "gc_count": gc_count,
            "gc_time_ms": gc_time,
            "heap_before_mb": int((heap_percent / 100) * HEAP_MAX_MB),
            "heap_after_mb": int(((heap_percent - 2) / 100) * HEAP_MAX_MB),
            "heap_percent_before": round(heap_percent, 2),
            "heap_percent_after": round(heap_percent - 2, 2),
            "pause_time_ms": gc_time
        }
        
        gc_logs.append(log)
    
    filepath = DATA_DIR / "logs" / "infra" / "gc_logs.json"
    with open(filepath, 'w') as f:
        json.dump(gc_logs, f, indent=2)
    
    return gc_logs


def generate_application_logs():
    """Generate application logs with errors appearing as heap grows"""
    logs = []
    total_minutes = 5 * 60 + 1
    
    error_messages = [
        "OutOfMemoryError: Java heap space",
        "GC overhead limit exceeded",
        "Unable to create new native thread",
        "Session cache allocation failed",
        "Payment context cache size exceeds threshold",
        "Memory allocation failure in SessionCacheManager"
    ]
    
    warning_messages = [
        "High heap usage detected: {}%",
        "GC frequency increasing",
        "Response time degradation observed",
        "Session cache growing rapidly",
        "Memory pressure warning"
    ]
    
    for minute in range(0, total_minutes, 3):  # Every 3 minutes
        timestamp = START_TIME + timedelta(minutes=minute)
        heap_percent = calculate_heap_percent(minute)
        
        if heap_percent > 85:
            # Critical errors
            log_level = "ERROR"
            message = random.choice(error_messages)
        elif heap_percent > 75:
            # Warnings
            log_level = "WARN"
            message = random.choice(warning_messages).format(int(heap_percent))
        else:
            # Info logs
            log_level = "INFO"
            message = "Payment processing completed successfully"
        
        log = {
            "@timestamp": timestamp.isoformat(),
            "app_id": APP_ID,
            "app_name": APP_NAME,
            "log_level": log_level,
            "message": message,
            "thread": f"http-nio-8080-exec-{random.randint(1, 50)}",
            "class": "com.westpac.payment.service.PaymentProcessor",
            "host": "payment-api-prod-03"
        }
        
        logs.append(log)
    
    filepath = DATA_DIR / "logs" / "app" / "application_logs.json"
    with open(filepath, 'w') as f:
        json.dump(logs, f, indent=2)
    
    return logs


def generate_traces():
    """Generate APM traces showing response time degradation"""
    traces = []
    total_minutes = 5 * 60 + 1
    
    for minute in range(0, total_minutes, 2):  # Every 2 minutes
        timestamp = START_TIME + timedelta(minutes=minute)
        heap_percent = calculate_heap_percent(minute)
        
        # Response time increases with heap pressure
        if heap_percent < 70:
            duration_ms = random.randint(100, 200)
        elif heap_percent < 80:
            duration_ms = random.randint(200, 500)
        elif heap_percent < 90:
            duration_ms = random.randint(500, 1500)
        else:
            duration_ms = random.randint(1500, 5000)
        
        trace = {
            "@timestamp": timestamp.isoformat(),
            "app_id": APP_ID,
            "trace_id": f"trace-{minute:04d}",
            "span_id": f"span-{minute:04d}",
            "operation": "POST /api/payment/process",
            "duration_ms": duration_ms,
            "status_code": 500 if heap_percent > 90 else 200,
            "error": heap_percent > 90,
            "error_type": "OutOfMemoryError" if heap_percent > 95 else None
        }
        
        traces.append(trace)
    
    filepath = DATA_DIR / "traces" / "apm_traces.json"
    with open(filepath, 'w') as f:
        json.dump(traces, f, indent=2)
    
    return traces


def generate_communications():
    """Generate Teams messages and emails about slowness"""
    comms = []
    
    # Teams messages
    teams_messages = [
        {
            "timestamp": (START_TIME + timedelta(hours=3)).isoformat(),
            "channel": "payments-support",
            "author": "Sarah Chen",
            "message": "Anyone else seeing slow responses from PaymentService API? Customers reporting delays.",
            "incident_ref": None
        },
        {
            "timestamp": (START_TIME + timedelta(hours=4)).isoformat(),
            "channel": "payments-support",
            "author": "Mike Johnson",
            "message": "Heap usage is climbing steadily since this morning's deployment. Currently at 78%.",
            "incident_ref": None
        },
        {
            "timestamp": ALERT_TIME.isoformat(),
            "channel": "alerts",
            "author": "AlertBot",
            "message": f"🚨 CRITICAL: JVM Heap > 85% for {APP_NAME} ({APP_ID})",
            "incident_ref": INCIDENT_ID
        },
        {
            "timestamp": (ALERT_TIME + timedelta(minutes=15)).isoformat(),
            "channel": "payments-support",
            "author": "Sarah Chen",
            "message": f"Created {INCIDENT_ID}. Looks like memory leak in new caching code.",
            "incident_ref": INCIDENT_ID
        }
    ]
    
    for msg in teams_messages:
        filepath = DATA_DIR / "comms" / "teams" / f"msg_{msg['timestamp'].replace(':', '-')}.json"
        with open(filepath, 'w') as f:
            json.dump(msg, f, indent=2)
        comms.append(msg)
    
    return comms


def generate_incident():
    """Generate incident record (created by alert)"""
    incident = {
        "incident_id": INCIDENT_ID,
        "app_id": APP_ID,
        "app_name": APP_NAME,
        "title": f"{APP_NAME} - Memory Leak - JVM Heap Exhaustion",
        "description": "Automated alert detected critical JVM heap usage (>85%). Progressive memory growth since v3.1.0 deployment at 08:00. System experiencing OOM errors and severe performance degradation.",
        "severity": "P1",
        "status": "resolved",
        "created_at": ALERT_TIME.isoformat(),
        "created_by": "alert-automation",
        "resolved_at": RESOLUTION_TIME.isoformat(),
        "resolved_by": "platform-team",
        "incident_type": "performance",
        "root_cause_category": "memory_leak",
        "impacted_users": "~8000",
        "business_impact": "Payment processing delays, transaction failures",
        "related_change": CHANGE_ID,
        "alert_triggered": True,
        "automated_rca": True
    }
    
    filepath = DATA_DIR / "incidents" / f"{INCIDENT_ID}.json"
    with open(filepath, 'w') as f:
        json.dump(incident, f, indent=2)
    
    return incident


def generate_alert_records():
    """Generate alert firing and resolution records"""
    alerts = [
        {
            "alert_id": "ALERT-MEM-001",
            "alert_name": "JVM Heap Memory Critical",
            "app_id": APP_ID,
            "alert_timestamp": ALERT_TIME.isoformat(),
            "threshold_value": 87.3,
            "threshold_config": 85.0,
            "alert_status": "firing",
            "severity": "critical",
            "incident_created": INCIDENT_ID
        },
        {
            "alert_id": "ALERT-MEM-001",
            "alert_name": "JVM Heap Memory Critical",
            "app_id": APP_ID,
            "alert_timestamp": RESOLUTION_TIME.isoformat(),
            "threshold_value": 42.1,
            "threshold_config": 85.0,
            "alert_status": "resolved",
            "severity": "critical",
            "incident_ref": INCIDENT_ID
        }
    ]
    
    for i, alert in enumerate(alerts):
        filepath = DATA_DIR / "alerts" / f"alert_{i+1}.json"
        with open(filepath, 'w') as f:
            json.dump(alert, f, indent=2)
    
    return alerts


def generate_knowledge_base():
    """Generate knowledge base article about memory leaks"""
    kb = {
        "kb_id": "KB-8934",
        "title": "Troubleshooting Java Memory Leaks in Microservices",
        "category": "performance",
        "tags": ["memory", "jvm", "performance", "troubleshooting"],
        "content": """
Common causes of memory leaks in Java applications:
1. Unclosed resources (connections, streams, files)
2. Static collections that grow unbounded
3. Cache implementations without eviction policies
4. Thread-local variables not cleared
5. Listeners/callbacks not deregistered

Investigation steps:
- Monitor heap usage trends over time
- Analyze GC logs for increasing frequency
- Take heap dumps and analyze with MAT/VisualVM
- Review recent code changes for resource management
- Check for unbounded caches or collections

Resolution strategies:
- Implement proper cache eviction policies
- Add memory limits to collections
- Ensure resources are closed in finally blocks
- Use weak references where appropriate
- Add heap monitoring alerts
        """,
        "created_at": "2025-11-15T10:00:00+11:00",
        "updated_at": "2026-01-20T14:30:00+11:00",
        "author": "Platform Engineering Team"
    }
    
    filepath = DATA_DIR / "knowledge" / "KB-8934.json"
    with open(filepath, 'w') as f:
        json.dump(kb, f, indent=2)
    
    return kb


def main():
    """Generate all data for Scenario 2"""
    print("=" * 70)
    print("SCENARIO 2: MEMORY LEAK DATA GENERATION")
    print("=" * 70)
    print(f"App: {APP_NAME} ({APP_ID})")
    print(f"Incident: {INCIDENT_ID}")
    print(f"Timeline: {START_TIME.strftime('%Y-%m-%d %H:%M')} → {RESOLUTION_TIME.strftime('%H:%M')}")
    print(f"Duration: 5 hours 15 minutes")
    print(f"Data Directory: {DATA_DIR}")
    print("=" * 70)
    print()
    
    ensure_directories()
    
    # Generate all data
    print("Generating data...")
    change = generate_change()
    print(f"✓ Change: {CHANGE_ID}")
    
    metrics = generate_memory_metrics()
    print(f"✓ Memory metrics: {len(metrics)} records (1 per minute)")
    
    gc_logs = generate_gc_logs()
    print(f"✓ GC logs: {len(gc_logs)} records")
    
    app_logs = generate_application_logs()
    print(f"✓ Application logs: {len(app_logs)} records")
    
    traces = generate_traces()
    print(f"✓ APM traces: {len(traces)} records")
    
    comms = generate_communications()
    print(f"✓ Communications: {len(comms)} records")
    
    incident = generate_incident()
    print(f"✓ Incident: {INCIDENT_ID}")
    
    alerts = generate_alert_records()
    print(f"✓ Alerts: {len(alerts)} records")
    
    kb = generate_knowledge_base()
    print(f"✓ Knowledge base: {kb['kb_id']}")
    
    print()
    print("=" * 70)
    total_docs = len(metrics) + len(gc_logs) + len(app_logs) + len(traces) + len(comms) + 1 + len(alerts) + 1 + 1
    print(f"✅ GENERATION COMPLETE: {total_docs} documents created")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run: python scripts/data_ingestion/ingest_scenario2_data.py")
    print(f"2. Verify in Kibana Discover: app_id:\"{APP_ID}\"")
    print("3. Check time range: Feb 4, 2026 08:00-13:00")


if __name__ == "__main__":
    main()
