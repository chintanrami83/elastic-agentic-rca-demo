#!/usr/bin/env python3
"""
Test Elasticsearch Connectivity
Verifies connection to Elastic Cloud and displays cluster information
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scripts.utilities.es_client import ElasticsearchClient
from rich.console import Console
from rich.table import Table
import logging

console = Console()


def test_connectivity():
    """Test Elasticsearch connectivity and display information"""
    
    console.print("\n[bold blue]Testing Elasticsearch Connectivity...[/bold blue]\n")
    
    try:
        # Test connection
        info = ElasticsearchClient.test_connection()
        
        # Display connection info
        table = Table(title="Elasticsearch Connection Details")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", "✓ Connected")
        table.add_row("Version", info['version'])
        table.add_row("Cluster Name", info['cluster_name'])
        table.add_row("Cluster UUID", info['cluster_uuid'])
        
        console.print(table)
        
        # Test ML capabilities
        es = ElasticsearchClient.get_client()
        
        try:
            ml_info = es.ml.info()
            console.print("\n[green]✓ ML Node Available[/green]")
            
            # Check for ELSER model
            try:
                models = es.ml.get_trained_models(model_id=".elser*")
                if models['trained_model_configs']:
                    model_id = models['trained_model_configs'][0]['model_id']
                    console.print(f"[green]✓ ELSER Model Found: {model_id}[/green]")
                else:
                    console.print("[yellow]⚠ ELSER Model Not Found - will need to deploy[/yellow]")
            except Exception as e:
                console.print(f"[yellow]⚠ Could not check ELSER model: {e}[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]⚠ ML Node: {e}[/yellow]")
        
        # Check existing indices
        console.print("\n[bold]Checking for existing indices...[/bold]")
        indices = es.indices.get_alias(index="*servicenow*,*logs*,*traces*,*comms*,*docs*,*code*")
        
        if indices:
            index_table = Table(title="Existing Indices")
            index_table.add_column("Index Name", style="cyan")
            index_table.add_column("Document Count", style="yellow")
            
            for index_name in sorted(indices.keys()):
                if not index_name.startswith('.'):  # Skip system indices
                    try:
                        count = es.count(index=index_name)['count']
                        index_table.add_row(index_name, f"{count:,}")
                    except:
                        index_table.add_row(index_name, "N/A")
            
            console.print(index_table)
        else:
            console.print("[yellow]No demo indices found yet[/yellow]")
        
        console.print("\n[bold green]✓ Connectivity test passed![/bold green]\n")
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Connection failed:[/bold red] {e}\n")
        console.print("[yellow]Please check your .env file configuration:[/yellow]")
        console.print("  - ELASTIC_URL")
        console.print("  - ELASTIC_USERNAME")
        console.print("  - ELASTIC_PASSWORD")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    success = test_connectivity()
    sys.exit(0 if success else 1)
