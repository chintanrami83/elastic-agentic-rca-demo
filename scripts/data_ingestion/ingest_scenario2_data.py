"""
Ingest Scenario 2 (Memory Leak) data into Elasticsearch
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utilities.es_client import get_es_client

# Configuration
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic" / "scenario2_memory_leak"


def ingest_json_files(es, directory, index_name):
    """Ingest all JSON files from a directory into specified index"""
    if not directory.exists():
        print(f"⚠ Directory not found: {directory}")
        return 0
    
    json_files = list(directory.glob("*.json"))
    if not json_files:
        print(f"⚠ No JSON files found in: {directory}")
        return 0
    
    count = 0
    for filepath in json_files:
        with open(filepath, 'r') as f:
            data = json.load(f)
            
            # Handle both single documents and arrays
            if isinstance(data, list):
                for doc in data:
                    es.index(index=index_name, document=doc)
                    count += 1
            else:
                es.index(index=index_name, document=data)
                count += 1
    
    return count


def main():
    """Ingest all Scenario 2 data"""
    print("=" * 70)
    print("SCENARIO 2: MEMORY LEAK DATA INGESTION")
    print("=" * 70)
    print(f"Data source: {DATA_DIR}")
    print()
    
    # Connect to Elasticsearch
    print("Connecting to Elasticsearch...")
    es = get_es_client()
    print(f"✓ Connected to: {es.info()['cluster_name']}")
    print()
    
    # Ingest data
    print("Ingesting data...")
    
    total_docs = 0
    
    # Incidents
    count = ingest_json_files(es, DATA_DIR / "incidents", "rca-incidents")
    print(f"✓ Incidents: {count} documents → rca-incidents")
    total_docs += count
    
    # Changes
    count = ingest_json_files(es, DATA_DIR / "changes", "rca-changes")
    print(f"✓ Changes: {count} documents → rca-changes")
    total_docs += count
    
    # Memory Metrics
    count = ingest_json_files(es, DATA_DIR / "metrics", "rca-metrics")
    print(f"✓ Memory Metrics: {count} documents → rca-metrics")
    total_docs += count
    
    # GC Logs
    count = ingest_json_files(es, DATA_DIR / "logs" / "infra", "rca-logs-infra")
    print(f"✓ GC Logs: {count} documents → rca-logs-infra")
    total_docs += count
    
    # Application Logs
    count = ingest_json_files(es, DATA_DIR / "logs" / "app", "rca-logs-app")
    print(f"✓ Application Logs: {count} documents → rca-logs-app")
    total_docs += count
    
    # Traces
    count = ingest_json_files(es, DATA_DIR / "traces", "rca-traces")
    print(f"✓ APM Traces: {count} documents → rca-traces")
    total_docs += count
    
    # Communications (Teams)
    count = ingest_json_files(es, DATA_DIR / "comms" / "teams", "rca-comms-teams")
    print(f"✓ Teams Messages: {count} documents → rca-comms-teams")
    total_docs += count
    
    # Communications (Email)
    count = ingest_json_files(es, DATA_DIR / "comms" / "email", "rca-comms-email")
    print(f"✓ Emails: {count} documents → rca-comms-email")
    total_docs += count
    
    # Knowledge Base
    count = ingest_json_files(es, DATA_DIR / "knowledge", "rca-knowledge")
    print(f"✓ Knowledge Base: {count} documents → rca-knowledge")
    total_docs += count
    
    # Alerts
    count = ingest_json_files(es, DATA_DIR / "alerts", "rca-alerts")
    print(f"✓ Alerts: {count} documents → rca-alerts")
    total_docs += count
    
    print()
    print("=" * 70)
    print(f"✅ INGESTION COMPLETE: {total_docs} documents indexed")
    print("=" * 70)
    print()
    print("Verification:")
    print('1. Go to Kibana Discover')
    print('2. Search: app_id:"APP-9123"')
    print('3. Time range: Feb 4, 2026 08:00-14:00')
    print(f'4. Expected: ~{total_docs} documents')
    print()
    print("View memory trends:")
    print('- Search: app_id:"APP-9123" AND metric_type:"jvm.memory.heap"')
    print('- Visualize heap_percent field over time')


if __name__ == "__main__":
    main()
