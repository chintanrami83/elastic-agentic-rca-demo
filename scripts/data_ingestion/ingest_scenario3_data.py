"""
Scenario 3 Data Ingestion Script
Ingests cascading timeout incident data into Elasticsearch
"""

import json
import sys
from pathlib import Path
from elasticsearch import Elasticsearch, helpers

# Add utilities to path
sys.path.append(str(Path(__file__).parent.parent))
from utilities.es_client import get_es_client

# Data source directory
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic" / "scenario3_cascading_timeout"

# Index mappings
INDEX_MAPPINGS = {
    "incidents": "rca-incidents",
    "alerts": "rca-alerts",
    "metrics": "rca-metrics",
    "logs/app": "rca-logs-app",
    "logs/infra": "rca-logs-infra",
    "traces": "rca-traces",
    "comms/teams": "rca-comms-teams",
    "comms/email": "rca-comms-email",
    "knowledge": "rca-knowledge"
}


def load_json_files(directory):
    """Load all JSON files from a directory"""
    documents = []
    dir_path = DATA_DIR / directory
    
    if not dir_path.exists():
        return documents
    
    for json_file in dir_path.glob("*.json"):
        with open(json_file, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                documents.extend(data)
            else:
                documents.append(data)
    
    return documents


def ingest_data(es, directory, index_name):
    """Ingest documents into specified index"""
    documents = load_json_files(directory)
    
    if not documents:
        print(f"⚠ No JSON files found in: {DATA_DIR / directory}")
        return 0
    
    # Prepare bulk actions
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]
    
    # Bulk index
    success, failed = helpers.bulk(es, actions, raise_on_error=False)
    
    if failed:
        print(f"⚠ {failed} documents failed to index")
    
    print(f"✓ {directory}: {success} documents → {index_name}")
    return success


def main():
    """Main ingestion function"""
    print("=" * 70)
    print("SCENARIO 3: CASCADING TIMEOUT DATA INGESTION")
    print("=" * 70)
    print(f"Data source: {DATA_DIR}")
    print()
    
    # Connect to Elasticsearch
    print("Connecting to Elasticsearch...")
    try:
        es = get_es_client()
        cluster_info = es.info()
        print(f"✓ Connected to: {cluster_info['cluster_name']}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return 1
    
    print()
    print("Ingesting data...")
    
    total_docs = 0
    
    # Ingest each data type
    for directory, index_name in INDEX_MAPPINGS.items():
        try:
            count = ingest_data(es, directory, index_name)
            total_docs += count
        except Exception as e:
            print(f"❌ Error ingesting {directory}: {e}")
    
    print()
    print("=" * 70)
    print(f"✅ INGESTION COMPLETE: {total_docs} documents indexed")
    print("=" * 70)
    print()
    print("Verification:")
    print("1. Go to Kibana Discover")
    print("2. Search: incident_id:\"INC0034567\"")
    print("3. Time range: Feb 3, 2026 14:00-16:30")
    print(f"4. Expected: ~950 documents")
    print()
    print("View cascading failure:")
    print("- Payment Service: app_id:\"APP-9123\"")
    print("- Inventory Service: app_id:\"APP-5521\"")  
    print("- OrderProcessing: app_id:\"APP-7654\"")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
