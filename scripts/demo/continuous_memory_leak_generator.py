"""
Continuous Memory Leak Data Generator for Scenario 2
Generates realistic JVM heap metrics every 60 seconds with gradual memory leak pattern
Perfect for live demo - shows real-time monitoring and alert triggering
"""

import json
import time
import sys
import signal
from datetime import datetime, timezone
from pathlib import Path
import random

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utilities.es_client import get_es_client

# Configuration
APP_ID = "APP-9123"
APP_NAME = "PaymentService API"
HEAP_MAX_MB = 4096
INDEX_NAME = "rca-metrics"

# Generator state file
STATE_FILE = Path(__file__).parent / "generator_state.json"

# Graceful shutdown handler
should_stop = False

def signal_handler(sig, frame):
    global should_stop
    print("\n⏸️  Graceful shutdown initiated...")
    should_stop = True

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def load_config():
    """Load configuration from config file"""
    config_file = Path(__file__).parent / "generator_config.json"
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            return json.load(f)
    
    # Default configuration
    return {
        "interval_seconds": 60,
        "heap_start_percent": 70.0,
        "heap_increase_per_cycle": 2.5,
        "heap_max_percent": 95.0,
        "alert_threshold": 85.0,
        "reset_after_max": True,
        "add_random_noise": True,
        "noise_range": 1.5
    }


def save_state(current_heap):
    """Save current state for resume capability"""
    state = {
        "last_heap_percent": current_heap,
        "last_run": datetime.now(timezone.utc).isoformat(),
        "total_metrics_generated": 1
    }
    
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            old_state = json.load(f)
            state["total_metrics_generated"] = old_state.get("total_metrics_generated", 0) + 1
    
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def load_state():
    """Load previous state if exists"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None


def generate_metric(heap_percent, config):
    """Generate a single memory metric document"""
    heap_used_mb = int((heap_percent / 100) * HEAP_MAX_MB)
    
    # Add realistic noise if configured
    if config["add_random_noise"]:
        noise = random.uniform(-config["noise_range"], config["noise_range"])
        heap_percent = max(0, min(100, heap_percent + noise))
        heap_used_mb = int((heap_percent / 100) * HEAP_MAX_MB)
    
    metric = {
        "@timestamp": datetime.now(timezone.utc).isoformat(),
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
        "environment": "production",
        "generated_by": "continuous_generator"
    }
    
    return metric


def display_status(heap_percent, threshold, cycle_count):
    """Display current status with visual indicators"""
    bar_length = 40
    filled = int((heap_percent / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    status_icon = "🟢" if heap_percent < threshold else "🔴"
    alert_status = "CRITICAL - ALERT FIRING" if heap_percent >= threshold else "NORMAL"
    
    print(f"\n{status_icon} Cycle #{cycle_count}")
    print(f"[{bar}] {heap_percent:.1f}%")
    print(f"Status: {alert_status}")
    print(f"Threshold: {threshold}%")
    
    if heap_percent >= threshold:
        print("⚠️  Alert condition met - workflow should trigger!")


def main():
    """Main generator loop"""
    global should_stop
    
    print("=" * 70)
    print("CONTINUOUS MEMORY LEAK DATA GENERATOR")
    print("=" * 70)
    print(f"App: {APP_NAME} ({APP_ID})")
    print(f"Index: {INDEX_NAME}")
    print("=" * 70)
    print()
    
    # Load configuration
    config = load_config()
    print("📋 Configuration:")
    print(f"   Interval: {config['interval_seconds']} seconds")
    print(f"   Start heap: {config['heap_start_percent']}%")
    print(f"   Increase per cycle: {config['heap_increase_per_cycle']}%")
    print(f"   Alert threshold: {config['alert_threshold']}%")
    print(f"   Max heap: {config['heap_max_percent']}%")
    print()
    
    # Connect to Elasticsearch
    print("🔌 Connecting to Elasticsearch...")
    try:
        es = get_es_client()
        cluster_info = es.info()
        print(f"✅ Connected to: {cluster_info['cluster_name']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1
    
    print()
    print("🚀 Starting continuous generation...")
    print("   Press Ctrl+C to stop gracefully")
    print("=" * 70)
    
    # Load previous state or start fresh
    state = load_state()
    if state:
        current_heap = state["last_heap_percent"]
        print(f"📊 Resuming from previous state: {current_heap:.1f}%")
    else:
        current_heap = config["heap_start_percent"]
        print(f"📊 Starting fresh at: {current_heap:.1f}%")
    
    cycle_count = 0
    
    # Main generation loop
    while not should_stop:
        cycle_count += 1
        
        # Generate and index metric
        try:
            metric = generate_metric(current_heap, config)
            es.index(index=INDEX_NAME, document=metric)
            
            # Display status
            display_status(current_heap, config["alert_threshold"], cycle_count)
            
            # Save state
            save_state(current_heap)
            
            # Calculate next heap percentage
            current_heap += config["heap_increase_per_cycle"]
            
            # Reset if exceeds max (simulate restart/recovery)
            if current_heap > config["heap_max_percent"]:
                if config["reset_after_max"]:
                    print("\n🔄 Max heap reached - simulating service restart...")
                    current_heap = config["heap_start_percent"]
                else:
                    current_heap = config["heap_max_percent"]
            
            # Wait for next cycle
            if not should_stop:
                print(f"\n⏱️  Next metric in {config['interval_seconds']} seconds...")
                time.sleep(config['interval_seconds'])
        
        except KeyboardInterrupt:
            should_stop = True
            break
        except Exception as e:
            print(f"\n❌ Error generating metric: {e}")
            print("   Retrying in 10 seconds...")
            time.sleep(10)
    
    # Graceful shutdown
    print("\n" + "=" * 70)
    print(f"✅ Generator stopped gracefully")
    print(f"   Total metrics generated: {cycle_count}")
    print(f"   Final heap level: {current_heap:.1f}%")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
