#!/usr/bin/env python3
"""
Ingest All Data - Elastic Agentic RCA Demo
Loads synthetic data into Elasticsearch indices
"""

import sys
import os
import json
from pathlib import Path
from elasticsearch.helpers import bulk

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scripts.utilities.es_client import get_es_client
from rich.console import Console
from rich.progress import Progress, track

console = Console()

# Data directory
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"

# Index mapping
INDEX_MAPPING = {
    "incidents": "rca-incidents",
    "changes": "rca-changes",
    "problems": "rca-problems",
    "logs": "rca-logs-app",  # Application logs
    "traces": "rca-traces",
    "comms": {
        "teams": "rca-comms-teams",
        "emails": "rca-comms-email"
    },
    "knowledge": "rca-knowledge",
    "code": "rca-code"
}


def load_json_file(filepath: Path) -> list:
    """Load JSON file"""
    if not filepath.exists():
        return []
    
    with open(filepath, 'r') as f:
        return json.load(f)


def bulk_index(es, index_name: str, documents: list):
    """Bulk index documents"""
    if not documents:
        console.print(f"  [yellow]⊘[/yellow] No documents for {index_name}")
        return 0
    
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in documents
    ]
    
    success, failed = bulk(es, actions, raise_on_error=False)
    console.print(f"  [green]✓[/green] Indexed {success} documents to {index_name}")
    
    if failed:
        console.print(f"  [red]✗[/red] Failed: {failed}")
    
    return success


def ingest_scenario(es, scenario_num: int):
    """Ingest all data for a scenario"""
    console.print(f"\n[bold]Ingesting Scenario {scenario_num}[/bold]")
    
    total_docs = 0
    
    # 1. Incidents
    incidents = load_json_file(DATA_DIR / "incidents" / f"scenario{scenario_num}_incidents.json")
    total_docs += bulk_index(es, INDEX_MAPPING["incidents"], incidents)
    
    # 2. Changes
    changes = load_json_file(DATA_DIR / "changes" / f"scenario{scenario_num}_changes.json")
    total_docs += bulk_index(es, INDEX_MAPPING["changes"], changes)
    
    # 3. Application Logs
    logs_app = load_json_file(DATA_DIR / "logs" / f"scenario{scenario_num}_logs_app.json")
    total_docs += bulk_index(es, INDEX_MAPPING["logs"], logs_app)
    
    # 4. Infrastructure Logs
    logs_infra = load_json_file(DATA_DIR / "logs" / f"scenario{scenario_num}_logs_infra.json")
    total_docs += bulk_index(es, "rca-logs-infra", logs_infra)
    
    # 5. Traces
    traces = load_json_file(DATA_DIR / "traces" / f"scenario{scenario_num}_traces.json")
    total_docs += bulk_index(es, INDEX_MAPPING["traces"], traces)
    
    # 6. Teams Messages
    teams = load_json_file(DATA_DIR / "comms" / f"scenario{scenario_num}_teams.json")
    total_docs += bulk_index(es, INDEX_MAPPING["comms"]["teams"], teams)
    
    # 7. Emails
    emails = load_json_file(DATA_DIR / "comms" / f"scenario{scenario_num}_emails.json")
    total_docs += bulk_index(es, INDEX_MAPPING["comms"]["emails"], emails)
    
    # 8. Knowledge Base
    kb = load_json_file(DATA_DIR / "knowledge" / f"scenario{scenario_num}_kb.json")
    total_docs += bulk_index(es, INDEX_MAPPING["knowledge"], kb)
    
    console.print(f"[green]✓ Scenario {scenario_num}: {total_docs} total documents[/green]")
    return total_docs


def main():
    """Main ingestion function"""
    
    console.print("\n[bold blue]═══════════════════════════════════════════[/bold blue]")
    console.print("[bold blue]  Elastic Agentic RCA Demo - Data Ingestion        [/bold blue]")
    console.print("[bold blue]═══════════════════════════════════════════[/bold blue]\n")
    
    try:
        # Get Elasticsearch client
        es = get_es_client()
        
        # Check connection
        info = es.info()
        console.print(f"[green]✓ Connected to Elasticsearch {info['version']['number']}[/green]")
        console.print(f"[green]✓ Cluster: {info['cluster_name']}[/green]\n")
        
        # Ingest all scenarios
        grand_total = 0
        
        # Scenario 1
        grand_total += ingest_scenario(es, 1)
        
        # TODO: Add scenarios 2 and 3 when generated
        
        # Refresh indices
        console.print("\n[bold]Refreshing indices...[/bold]")
        es.indices.refresh(index="rca-*")
        console.print("[green]✓ Indices refreshed[/green]")
        
        # Show document counts
        console.print("\n[bold]Document counts by index:[/bold]")
        for index in ["rca-incidents", "rca-changes", "rca-logs-app", "rca-logs-infra",
                      "rca-traces", "rca-comms-teams", "rca-comms-email", "rca-knowledge"]:
            try:
                count = es.count(index=index)['count']
                console.print(f"  {index}: [cyan]{count:,}[/cyan] documents")
            except:
                console.print(f"  {index}: [yellow]0[/yellow] documents")
        
        console.print(f"\n[bold green]Total ingested: {grand_total:,} documents[/bold green]")
        
        console.print("\n[bold green]═══════════════════════════════════════════[/bold green]")
        console.print("[bold green]  Data Ingestion Complete!                  [/bold green]")
        console.print("[bold green]═══════════════════════════════════════════[/bold green]\n")
        
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Verify data in Kibana:")
        console.print("     ${KIBANA_URL}")
        console.print("  2. Run demo scenario:")
        console.print("     python agents/orchestrator/main.py --incident INC0012345\n")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Ingestion failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
