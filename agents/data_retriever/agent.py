#!/usr/bin/env python3
"""
Agent 1: Data Retriever
Pure tool-based agent - queries Elasticsearch for all incident-related data

NO LLM - just intelligent Elasticsearch queries
"""

import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scripts.utilities.es_client import get_es_client
import pytz
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()
SYDNEY_TZ = pytz.timezone('Australia/Sydney')


class DataRetrieverAgent:
    """
    Agent 1: Data Retriever
    
    Responsibilities:
    - Retrieve incident record from Elasticsearch
    - Calculate relevant time windows
    - Query all related data sources (changes, logs, traces, comms)
    - Return structured data for correlation
    
    Tools:
    - elasticsearch_query
    - time_range_calculator
    - multi_index_search
    """
    
    def __init__(self):
        self.es = get_es_client()
        self.name = "DataRetrieverAgent"
        
    def execute(self, incident_id: str) -> Dict[str, Any]:
        """
        Main execution method
        
        Args:
            incident_id: Incident ID to analyze (e.g., "INC0012345")
            
        Returns:
            Dictionary containing all retrieved data
        """
        console.print(f"\n[bold cyan]🤖 Agent 1: Data Retriever[/bold cyan]")
        console.print(f"[dim]Retrieving data for {incident_id}...[/dim]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Step 1: Get incident record
            task1 = progress.add_task("Retrieving incident record...", total=None)
            incident = self._get_incident(incident_id)
            progress.update(task1, completed=True)
            
            if not incident:
                console.print(f"[red]✗ Incident {incident_id} not found[/red]")
                return {}
            
            console.print(f"  [green]✓[/green] Found incident: {incident.get('description', 'N/A')[:60]}...")
            
            # Step 2: Calculate time window
            task2 = progress.add_task("Calculating time window...", total=None)
            time_window = self._calculate_time_window(incident)
            progress.update(task2, completed=True)
            
            console.print(f"  [green]✓[/green] Time window: {time_window['start_readable']} → {time_window['end_readable']}")
            
            # Step 3: Get related changes
            task3 = progress.add_task("Querying changes...", total=None)
            changes = self._get_changes(incident, time_window)
            progress.update(task3, completed=True)
            console.print(f"  [green]✓[/green] Found {len(changes)} change(s)")
            
            # Step 4: Get application logs
            task4 = progress.add_task("Querying application logs...", total=None)
            logs_app = self._get_logs(incident, time_window, "rca-logs-app")
            progress.update(task4, completed=True)
            console.print(f"  [green]✓[/green] Found {len(logs_app)} application log(s)")
            
            # Step 5: Get infrastructure logs
            task5 = progress.add_task("Querying infrastructure logs...", total=None)
            logs_infra = self._get_logs(incident, time_window, "rca-logs-infra")
            progress.update(task5, completed=True)
            console.print(f"  [green]✓[/green] Found {len(logs_infra)} infrastructure log(s)")
            
            # Step 6: Get traces
            task6 = progress.add_task("Querying APM traces...", total=None)
            traces = self._get_traces(incident, time_window)
            progress.update(task6, completed=True)
            console.print(f"  [green]✓[/green] Found {len(traces)} trace(s)")
            
            # Step 7: Get communications
            task7 = progress.add_task("Querying communications...", total=None)
            comms = self._get_communications(incident_id)
            progress.update(task7, completed=True)
            console.print(f"  [green]✓[/green] Found {comms['teams_count'] + comms['email_count']} communication(s)")
        
        # Compile results
        results = {
            "incident": incident,
            "time_window": time_window,
            "changes": changes,
            "logs": {
                "application": logs_app,
                "infrastructure": logs_infra
            },
            "traces": traces,
            "communications": comms,
            "metadata": {
                "total_documents": (
                    1 +  # incident
                    len(changes) +
                    len(logs_app) +
                    len(logs_infra) +
                    len(traces) +
                    comms['teams_count'] +
                    comms['email_count']
                ),
                "retrieval_time": datetime.now(SYDNEY_TZ).isoformat()
            }
        }
        
        console.print(f"\n[bold green]✓ Data retrieval complete[/bold green]")
        console.print(f"[dim]Total documents: {results['metadata']['total_documents']}[/dim]\n")
        
        return results
    
    def _get_incident(self, incident_id: str) -> Dict[str, Any]:
        """Retrieve incident record from Elasticsearch"""
        try:
            result = self.es.search(
                index="rca-incidents",
                query={
                    "term": {"incident_id": incident_id}
                },
                size=1
            )
            
            if result['hits']['total']['value'] > 0:
                return result['hits']['hits'][0]['_source']
            return None
            
        except Exception as e:
            console.print(f"[red]Error retrieving incident: {e}[/red]")
            return None
    
    def _calculate_time_window(self, incident: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate time window for searching related data
        
        Window: 24 hours before incident → resolution time (or +6 hours if not resolved)
        """
        created_at = datetime.fromisoformat(incident['created_at'].replace('+11:00', ''))
        created_at = SYDNEY_TZ.localize(created_at) if created_at.tzinfo is None else created_at
        
        # Start: 24 hours before incident
        start_time = created_at - timedelta(hours=24)
        
        # End: Resolution time or 6 hours after creation
        if incident.get('resolved_at'):
            end_time = datetime.fromisoformat(incident['resolved_at'].replace('+11:00', ''))
            end_time = SYDNEY_TZ.localize(end_time) if end_time.tzinfo is None else end_time
        else:
            end_time = created_at + timedelta(hours=6)
        
        return {
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "start_readable": start_time.strftime("%Y-%m-%d %H:%M %Z"),
            "end_readable": end_time.strftime("%Y-%m-%d %H:%M %Z"),
            "duration_hours": (end_time - created_at).total_seconds() / 3600
        }
    
    def _get_changes(self, incident: Dict[str, Any], time_window: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get changes related to this incident"""
        try:
            result = self.es.search(
                index="rca-changes",
                query={
                    "bool": {
                        "must": [
                            {"term": {"app_id": incident['app_id']}},
                            {
                                "range": {
                                    "implemented_at": {
                                        "gte": time_window['start'],
                                        "lte": time_window['end']
                                    }
                                }
                            }
                        ]
                    }
                },
                sort=[{"implemented_at": "asc"}],
                size=50
            )
            
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            console.print(f"[red]Error retrieving changes: {e}[/red]")
            return []
    
    def _get_logs(self, incident: Dict[str, Any], time_window: Dict[str, Any], index: str) -> List[Dict[str, Any]]:
        """Get logs from specified index"""
        try:
            result = self.es.search(
                index=index,
                query={
                    "bool": {
                        "must": [
                            {"term": {"app_id": incident['app_id']}},
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": time_window['start'],
                                        "lte": time_window['end']
                                    }
                                }
                            }
                        ]
                    }
                },
                sort=[{"@timestamp": "asc"}],
                size=500  # Limit to prevent overwhelming data
            )
            
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            console.print(f"[red]Error retrieving logs from {index}: {e}[/red]")
            return []
    
    def _get_traces(self, incident: Dict[str, Any], time_window: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get APM traces"""
        try:
            result = self.es.search(
                index="rca-traces",
                query={
                    "bool": {
                        "must": [
                            {"term": {"app_id": incident['app_id']}},
                            {
                                "range": {
                                    "@timestamp": {
                                        "gte": time_window['start'],
                                        "lte": time_window['end']
                                    }
                                }
                            }
                        ]
                    }
                },
                sort=[{"@timestamp": "asc"}],
                size=500
            )
            
            return [hit['_source'] for hit in result['hits']['hits']]
            
        except Exception as e:
            console.print(f"[red]Error retrieving traces: {e}[/red]")
            return []
    
    def _get_communications(self, incident_id: str) -> Dict[str, Any]:
        """Get Teams messages and emails"""
        teams_messages = []
        emails = []
        
        # Teams messages
        try:
            result = self.es.search(
                index="rca-comms-teams",
                query={"term": {"incident_ref": incident_id}},
                sort=[{"@timestamp": "asc"}],
                size=100
            )
            teams_messages = [hit['_source'] for hit in result['hits']['hits']]
        except Exception as e:
            console.print(f"[yellow]Warning: Could not retrieve Teams messages: {e}[/yellow]")
        
        # Emails
        try:
            result = self.es.search(
                index="rca-comms-email",
                query={"term": {"incident_ref": incident_id}},
                sort=[{"@timestamp": "asc"}],
                size=100
            )
            emails = [hit['_source'] for hit in result['hits']['hits']]
        except Exception as e:
            console.print(f"[yellow]Warning: Could not retrieve emails: {e}[/yellow]")
        
        return {
            "teams": teams_messages,
            "emails": emails,
            "teams_count": len(teams_messages),
            "email_count": len(emails)
        }


def main():
    """Test the agent"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Retriever Agent - Test")
    parser.add_argument('--incident', default='INC0012345', help='Incident ID to analyze')
    args = parser.parse_args()
    
    # Create and run agent
    agent = DataRetrieverAgent()
    results = agent.execute(args.incident)
    
    # Display summary
    if results:
        console.print("\n[bold]📊 Summary:[/bold]")
        console.print(f"  Incident: {results['incident']['incident_id']}")
        console.print(f"  Application: {results['incident']['app_id']}")
        console.print(f"  Severity: {results['incident']['severity']}")
        console.print(f"  Changes found: {len(results['changes'])}")
        console.print(f"  Total logs: {len(results['logs']['application']) + len(results['logs']['infrastructure'])}")
        console.print(f"  Traces: {len(results['traces'])}")
        console.print(f"  Communications: {results['communications']['teams_count'] + results['communications']['email_count']}")
        console.print(f"\n[green]✓ Agent 1 execution successful![/green]\n")


if __name__ == "__main__":
    main()
