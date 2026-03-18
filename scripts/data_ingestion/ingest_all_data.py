#!/usr/bin/env python3
"""
Ingest All Data - Elastic Agentic RCA Demo
Loads synthetic data for all 3 scenarios into Elasticsearch
"""

import sys
import os
import json
from pathlib import Path
from elasticsearch.helpers import bulk

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scripts.utilities.es_client import get_es_client
from rich.console import Console

console = Console()

DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"


def load_json_file(filepath: Path) -> list:
    if not filepath.exists():
        return []
    with open(filepath, 'r') as f:
        data = json.load(f)
        return data if isinstance(data, list) else [data]


def load_json_dir(dirpath: Path) -> list:
    docs = []
    if not dirpath.exists():
        return docs
    for f in dirpath.glob("*.json"):
        with open(f, 'r') as fh:
            data = json.load(fh)
            if isinstance(data, list):
                docs.extend(data)
            else:
                docs.append(data)
    return docs


def bulk_index(es, index_name: str, documents: list) -> int:
    if not documents:
        console.print(f"  [yellow]⊘[/yellow] No documents for {index_name}")
        return 0
    actions = [{"_index": index_name, "_source": doc} for doc in documents]
    success, failed = bulk(es, actions, raise_on_error=False)
    console.print(f"  [green]✓[/green] {success} documents → {index_name}")
    if failed:
        console.print(f"  [red]✗[/red] {len(failed)} failed")
    return success


def ingest_scenario1(es) -> int:
    console.print("\n[bold]Scenario 1 — DB Connection Pool Exhaustion[/bold]")
    total = 0
    base = DATA_DIR
    total += bulk_index(es, "rca-incidents",    load_json_file(base / "incidents/scenario1_incidents.json"))
    total += bulk_index(es, "rca-changes",      load_json_file(base / "changes/scenario1_changes.json"))
    total += bulk_index(es, "rca-logs-app",     load_json_file(base / "logs/scenario1_logs_app.json"))
    total += bulk_index(es, "rca-logs-infra",   load_json_file(base / "logs/scenario1_logs_infra.json"))
    total += bulk_index(es, "rca-traces",       load_json_file(base / "traces/scenario1_traces.json"))
    total += bulk_index(es, "rca-comms-teams",  load_json_file(base / "comms/scenario1_teams.json"))
    total += bulk_index(es, "rca-comms-email",  load_json_file(base / "comms/scenario1_emails.json"))
    total += bulk_index(es, "rca-knowledge",    load_json_file(base / "knowledge/scenario1_kb.json"))
    console.print(f"[green]✓ Scenario 1: {total} documents[/green]")
    return total


def ingest_scenario2(es) -> int:
    console.print("\n[bold]Scenario 2 — JVM Memory Leak[/bold]")
    total = 0
    base = DATA_DIR / "scenario2_memory_leak"
    total += bulk_index(es, "rca-incidents",    load_json_dir(base / "incidents"))
    total += bulk_index(es, "rca-changes",      load_json_dir(base / "changes"))
    total += bulk_index(es, "rca-alerts",       load_json_dir(base / "alerts"))
    total += bulk_index(es, "rca-logs-app",     load_json_dir(base / "logs/app"))
    total += bulk_index(es, "rca-logs-infra",   load_json_dir(base / "logs/infra"))
    total += bulk_index(es, "rca-metrics",      load_json_dir(base / "metrics"))
    total += bulk_index(es, "rca-traces",       load_json_dir(base / "traces"))
    total += bulk_index(es, "rca-comms-teams",  load_json_dir(base / "comms/teams"))
    total += bulk_index(es, "rca-knowledge",    load_json_dir(base / "knowledge"))
    console.print(f"[green]✓ Scenario 2: {total} documents[/green]")
    return total


def ingest_scenario3(es) -> int:
    console.print("\n[bold]Scenario 3 — Cascading Timeout[/bold]")
    total = 0
    base = DATA_DIR / "scenario3_cascading_timeout"
    total += bulk_index(es, "rca-incidents",    load_json_dir(base / "incidents"))
    total += bulk_index(es, "rca-alerts",       load_json_dir(base / "alerts"))
    total += bulk_index(es, "rca-logs-app",     load_json_dir(base / "logs/app"))
    total += bulk_index(es, "rca-metrics",      load_json_dir(base / "metrics"))
    total += bulk_index(es, "rca-traces",       load_json_dir(base / "traces"))
    total += bulk_index(es, "rca-comms-teams",  load_json_dir(base / "comms/teams"))
    total += bulk_index(es, "rca-knowledge",    load_json_dir(base / "knowledge"))
    console.print(f"[green]✓ Scenario 3: {total} documents[/green]")
    return total


def main():
    console.print("\n[bold blue]═══════════════════════════════════════════[/bold blue]")
    console.print("[bold blue]  Elastic Agentic RCA Demo — Data Ingestion[/bold blue]")
    console.print("[bold blue]═══════════════════════════════════════════[/bold blue]")

    try:
        es = get_es_client()
        info = es.info()
        console.print(f"\n[green]✓ Connected to Elasticsearch {info['version']['number']}[/green]")
        console.print(f"[green]✓ Cluster: {info['cluster_name']}[/green]")

        grand_total = 0
        grand_total += ingest_scenario1(es)
        grand_total += ingest_scenario2(es)
        grand_total += ingest_scenario3(es)

        # Refresh all rca-* indices
        es.indices.refresh(index="rca-*")

        # Show final counts
        console.print("\n[bold]Document counts by index:[/bold]")
        indices = ["rca-incidents", "rca-changes", "rca-alerts", "rca-logs-app",
                   "rca-logs-infra", "rca-metrics", "rca-traces",
                   "rca-comms-teams", "rca-comms-email", "rca-knowledge"]
        for idx in indices:
            try:
                count = es.count(index=idx)['count']
                if count > 0:
                    console.print(f"  {idx}: [cyan]{count:,}[/cyan]")
            except:
                pass

        console.print(f"\n[bold green]Total ingested: {grand_total:,} documents[/bold green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("  1. Open Kibana → Discover")
        console.print("  2. Create data view: index pattern [cyan]rca-*[/cyan], time field [cyan]@timestamp[/cyan]")
        console.print("  3. Search [cyan]incident_id:\"INC0012345\"[/cyan] to verify Scenario 1\n")
        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Ingestion failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
