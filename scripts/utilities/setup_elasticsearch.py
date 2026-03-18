#!/usr/bin/env python3
"""
Elasticsearch Setup Script - FIXED for Elastic Cloud 9.3
Creates all indices with names that don't conflict with built-in templates
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from scripts.utilities.es_client import get_es_client
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# FIXED: Renamed indices to avoid conflicts with built-in templates
# Old names like "logs-*" and "traces-*" conflict with Elastic's data stream templates
INDEX_MAPPINGS = {
    "rca-incidents": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "1s"
        },
        "mappings": {
            "properties": {
                "incident_id": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "severity": {"type": "keyword"},
                "created_at": {"type": "date"},
                "created_by": {"type": "keyword"},
                "description": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                },
                "affected_ci": {"type": "keyword"},
                "status": {"type": "keyword"},
                "resolved_at": {"type": "date"},
                "resolution_time_minutes": {"type": "integer"},
                "impact": {"type": "keyword"},
                "urgency": {"type": "keyword"},
                "category": {"type": "keyword"}
            }
        }
    },
    
    "rca-changes": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1,
            "refresh_interval": "1s"
        },
        "mappings": {
            "properties": {
                "change_id": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "change_type": {"type": "keyword"},
                "implemented_at": {"type": "date"},
                "description": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                },
                "implemented_by": {"type": "keyword"},
                "status": {"type": "keyword"},
                "risk_level": {"type": "keyword"},
                "affected_cis": {"type": "keyword"}
            }
        }
    },
    
    "rca-problems": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "problem_id": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "created_at": {"type": "date"},
                "description": {"type": "text"},
                "root_cause": {"type": "text"},
                "related_incidents": {"type": "keyword"},
                "status": {"type": "keyword"}
            }
        }
    },
    
    "rca-logs-infra": {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "5s"
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "log_level": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "host": {"type": "keyword"},
                "message": {"type": "text", "analyzer": "standard"},
                "stack_trace": {"type": "text"},
                "thread": {"type": "keyword"},
                "error_code": {"type": "keyword"},
                "cpu_percent": {"type": "float"},
                "memory_percent": {"type": "float"}
            }
        }
    },
    
    "rca-logs-app": {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1,
            "refresh_interval": "5s"
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "log_level": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "service_name": {"type": "keyword"},
                "message": {"type": "text"},
                "exception": {"type": "text"},
                "request_id": {"type": "keyword"},
                "user_id": {"type": "keyword"},
                "duration_ms": {"type": "long"}
            }
        }
    },
    
    "rca-traces": {
        "settings": {
            "number_of_shards": 2,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "app_id": {"type": "keyword"},
                "transaction_name": {"type": "keyword"},
                "duration_ms": {"type": "long"},
                "status": {"type": "keyword"},
                "db_time_ms": {"type": "long"},
                "error_message": {"type": "text"},
                "trace_id": {"type": "keyword"},
                "span_id": {"type": "keyword"}
            }
        }
    },
    
    "rca-comms-teams": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "channel": {"type": "keyword"},
                "sender": {"type": "keyword"},
                "message": {"type": "text"},
                "thread_id": {"type": "keyword"},
                "incident_ref": {"type": "keyword"},
                "mentions": {"type": "keyword"}
            }
        }
    },
    
    "rca-comms-email": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "@timestamp": {"type": "date"},
                "from": {"type": "keyword"},
                "to": {"type": "keyword"},
                "cc": {"type": "keyword"},
                "subject": {"type": "text"},
                "body": {"type": "text"},
                "incident_ref": {"type": "keyword"},
                "attachments": {"type": "keyword"}
            }
        }
    },
    
    "rca-knowledge": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "kb_id": {"type": "keyword"},
                "title": {"type": "text"},
                "content": {"type": "text"},
                "tags": {"type": "keyword"},
                "category": {"type": "keyword"},
                "last_updated": {"type": "date"},
                "view_count": {"type": "integer"},
                "helpful_count": {"type": "integer"}
            }
        }
    },
    
    "rca-code": {
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 1
        },
        "mappings": {
            "properties": {
                "file_path": {"type": "keyword"},
                "app_id": {"type": "keyword"},
                "language": {"type": "keyword"},
                "code": {"type": "text"},
                "commit_hash": {"type": "keyword"},
                "commit_date": {"type": "date"},
                "author": {"type": "keyword"}
            }
        }
    }
}


def create_index(es, index_name: str, config: dict, force: bool = False):
    """Create an index with given configuration"""
    
    if es.indices.exists(index=index_name):
        if force:
            console.print(f"  [yellow]Deleting existing index:[/yellow] {index_name}")
            es.indices.delete(index=index_name)
        else:
            console.print(f"  [yellow]Index already exists:[/yellow] {index_name}")
            return False
    
    console.print(f"  [green]Creating index:[/green] {index_name}")
    es.indices.create(index=index_name, **config)
    return True


def setup_ingest_pipeline(es):
    """Create ingest pipeline for log enrichment"""
    
    pipeline_id = "rca-logs-enrichment"
    
    pipeline = {
        "description": "Enrich log entries with metadata",
        "processors": [
            {
                "set": {
                    "field": "ingested_at",
                    "value": "{{_ingest.timestamp}}"
                }
            },
            {
                "lowercase": {
                    "field": "log_level",
                    "ignore_missing": True
                }
            }
        ]
    }
    
    console.print(f"  [green]Creating ingest pipeline:[/green] {pipeline_id}")
    es.ingest.put_pipeline(id=pipeline_id, body=pipeline)


def check_elser_model(es):
    """Check if ELSER model is deployed"""
    
    try:
        models = es.ml.get_trained_models(model_id=".elser*")
        if models['trained_model_configs']:
            model_id = models['trained_model_configs'][0]['model_id']
            console.print(f"  [green]✓ ELSER model found:[/green] {model_id}")
            return True
        else:
            console.print("  [yellow]⚠ ELSER model not found[/yellow]")
            console.print("    Optional: Deploy from Kibana → ML → Trained Models")
            return False
    except Exception as e:
        console.print(f"  [yellow]⚠ Could not check ELSER: {e}[/yellow]")
        return False


def main(force: bool = False):
    """Main setup function"""
    
    console.print("\n[bold blue]═══════════════════════════════════════════[/bold blue]")
    console.print("[bold blue]   Elastic Agentic RCA Demo - Elasticsearch Setup   [/bold blue]")
    console.print("[bold blue]   (Fixed for Elastic Cloud 9.3)            [/bold blue]")
    console.print("[bold blue]═══════════════════════════════════════════[/bold blue]\n")
    
    try:
        # Get Elasticsearch client
        es = get_es_client()
        
        # Check connection
        info = es.info()
        console.print(f"[green]✓ Connected to Elasticsearch {info['version']['number']}[/green]")
        console.print(f"[green]✓ Cluster: {info['cluster_name']}[/green]\n")
        
        # Create indices
        console.print("[bold]Creating indices with RCA prefix...[/bold]")
        console.print("[dim]Using 'rca-*' naming to avoid built-in template conflicts[/dim]\n")
        created_count = 0
        
        for index_name, config in INDEX_MAPPINGS.items():
            if create_index(es, index_name, config, force):
                created_count += 1
        
        console.print(f"\n[green]✓ Created {created_count} indices[/green]\n")
        
        # Setup ingest pipeline
        console.print("[bold]Setting up ingest pipelines...[/bold]")
        setup_ingest_pipeline(es)
        console.print()
        
        # Check ELSER model
        console.print("[bold]Checking ML configuration...[/bold]")
        check_elser_model(es)
        console.print()
        
        # Summary
        console.print("[bold green]═══════════════════════════════════════════[/bold green]")
        console.print("[bold green]   Setup Complete!   [/bold green]")
        console.print("[bold green]═══════════════════════════════════════════[/bold green]\n")
        
        console.print("[bold]Indices created:[/bold]")
        for idx in INDEX_MAPPINGS.keys():
            console.print(f"  ✓ {idx}")
        console.print()
        
        console.print("[bold]Next steps:[/bold]")
        console.print("  1. Generate synthetic data:")
        console.print("     python scripts/data_generation/generate_all_scenarios.py")
        console.print("  2. Ingest data into Elasticsearch:")
        console.print("     python scripts/data_ingestion/ingest_all_data.py")
        console.print("  3. Run a demo scenario:")
        console.print("     python agents/orchestrator/main.py --incident INC0012345\n")
        
        return True
        
    except Exception as e:
        console.print(f"\n[bold red]✗ Setup failed:[/bold red] {e}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup Elasticsearch for Elastic Agentic RCA Demo")
    parser.add_argument('--force', action='store_true', help='Delete and recreate existing indices')
    args = parser.parse_args()
    
    success = main(force=args.force)
    sys.exit(0 if success else 1)
