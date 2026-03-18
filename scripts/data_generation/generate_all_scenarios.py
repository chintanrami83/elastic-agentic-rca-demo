#!/usr/bin/env python3
"""
Generate All Scenarios - Westpac RCA Demo
UPDATED: Uses current dates (Feb 4, 2026)
Creates synthetic data with timestamps from TODAY
"""

import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from faker import Faker
import pytz
from rich.console import Console

fake = Faker()
console = Console()

# Sydney timezone
SYDNEY_TZ = pytz.timezone('Australia/Sydney')

# Data output directory
DATA_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic"

# Common people for consistency
TEAM_MEMBERS = [
    "john.smith@westpac.com",
    "sarah.chen@westpac.com",
    "marcus.liu@westpac.com",
    "emily.johnson@westpac.com",
    "david.kumar@westpac.com",
    "lisa.wong@westpac.com"
]

# Common hosts
HOSTS = [
    "customerportal-api-pod-1",
    "customerportal-api-pod-2",
    "paymentservice-pod-1",
    "paymentservice-pod-2",
    "api-gateway-pod-1",
    "db-prod-01",
    "db-prod-02"
]


def format_datetime(dt: datetime) -> str:
    """Format datetime to ISO string"""
    if dt.tzinfo is None:
        dt = SYDNEY_TZ.localize(dt)
    return dt.isoformat()


def save_json(data: list, filepath: Path):
    """Save data as JSON"""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2, default=str)
    console.print(f"  [green]✓[/green] Saved {len(data)} documents to {filepath.name}")


def generate_scenario_1():
    """
    Scenario 1: Database Connection Pool Exhaustion
    CustomerPortal-API, Feb 4, 2026 (TODAY)
    Incident happened this morning, resolved by 11 AM
    """
    console.print("\n[bold]Generating Scenario 1: Connection Pool Exhaustion[/bold]")
    console.print("[dim]Timeline: Feb 4, 2026 - This morning (08:00-11:00)[/dim]\n")
    
    app_id = "APP-2847"
    incident_id = "INC0012345"
    change_id = "CHG0089234"
    
    # Timeline - TODAY (Feb 4, 2026)
    today = datetime.now(SYDNEY_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    
    change_time = today.replace(hour=8, minute=0)      # 08:00 AM today
    first_error = today.replace(hour=8, minute=30)     # 08:30 AM
    incident_created = today.replace(hour=9, minute=0)  # 09:00 AM
    resolution = today.replace(hour=11, minute=0)       # 11:00 AM
    
    # 1. Incident
    incidents = [{
        "incident_id": incident_id,
        "app_id": app_id,
        "severity": "P1",
        "created_at": format_datetime(incident_created),
        "created_by": "john.smith@westpac.com",
        "description": "CustomerPortal API returning 500 errors - connection pool exhausted",
        "affected_ci": "CustomerPortal-API-PROD",
        "status": "Resolved",
        "resolved_at": format_datetime(resolution),
        "resolution_time_minutes": 120,
        "impact": "High",
        "urgency": "High",
        "category": "Availability"
    }]
    save_json(incidents, DATA_DIR / "incidents" / "scenario1_incidents.json")
    
    # 2. Changes
    changes = [
        {
            "change_id": change_id,
            "app_id": app_id,
            "change_type": "Standard",
            "implemented_at": format_datetime(change_time),
            "description": "Deploy v2.3.1 - traffic optimization features",
            "implemented_by": "deploy-automation",
            "status": "Successful",
            "risk_level": "Medium",
            "affected_cis": ["CustomerPortal-API-PROD"]
        },
        {
            "change_id": "CHG0089235",
            "app_id": app_id,
            "change_type": "Emergency",
            "implemented_at": format_datetime(today.replace(hour=10, minute=30)),
            "description": "Update connection pool max size to 200",
            "implemented_by": "sarah.chen@westpac.com",
            "status": "Successful",
            "risk_level": "Low",
            "affected_cis": ["CustomerPortal-API-PROD"]
        }
    ]
    save_json(changes, DATA_DIR / "changes" / "scenario1_changes.json")
    
    # 3. Application Logs
    logs_app = []
    current = first_error
    error_rate = 0
    
    while current <= resolution:
        # Increase error rate after first_error, decrease after fix (10:30)
        fix_time = today.replace(hour=10, minute=30)
        if current < fix_time:
            error_rate = min(0.45, error_rate + 0.02)
        else:
            error_rate = max(0, error_rate - 0.1)
        
        # Generate logs
        for _ in range(random.randint(8, 15)):
            is_error = random.random() < error_rate
            
            log = {
                "@timestamp": format_datetime(current),
                "log_level": "ERROR" if is_error else random.choice(["INFO", "INFO", "INFO", "WARN"]),
                "app_id": app_id,
                "service_name": "CustomerPortal-API",
                "host": random.choice(HOSTS[:3]),
                "request_id": f"req-{fake.uuid4()[:8]}",
                "duration_ms": random.randint(100, 500) if not is_error else random.randint(5000, 15000)
            }
            
            if is_error:
                log["message"] = "java.sql.SQLException: Cannot get connection, pool exhausted"
                log["exception"] = "java.sql.SQLException"
            else:
                log["message"] = random.choice([
                    "Request processed successfully",
                    "API call completed",
                    "Transaction successful"
                ])
            
            logs_app.append(log)
        
        current += timedelta(minutes=5)
    
    save_json(logs_app[:1200], DATA_DIR / "logs" / "scenario1_logs_app.json")
    
    # 4. Infrastructure Logs
    logs_infra = []
    current = first_error
    
    while current <= resolution and len(logs_infra) < 850:
        log = {
            "@timestamp": format_datetime(current),
            "log_level": random.choice(["INFO", "WARN", "ERROR"]),
            "app_id": app_id,
            "host": random.choice(["db-prod-01", "db-prod-02"]),
            "message": random.choice([
                "Database connection established",
                "Connection pool status check",
                "High CPU utilization detected",
                "Memory usage at 75%"
            ]),
            "cpu_percent": random.uniform(60, 95) if current < fix_time else random.uniform(30, 60),
            "memory_percent": random.uniform(70, 85)
        }
        logs_infra.append(log)
        current += timedelta(minutes=random.randint(3, 8))
    
    save_json(logs_infra, DATA_DIR / "logs" / "scenario1_logs_infra.json")
    
    # 5. APM Traces
    traces = []
    current = first_error
    
    while current <= resolution and len(traces) < 450:
        is_slow = current < fix_time
        
        trace = {
            "@timestamp": format_datetime(current),
            "app_id": app_id,
            "transaction_name": random.choice([
                "GET /api/customers/{id}",
                "POST /api/transactions",
                "GET /api/accounts"
            ]),
            "duration_ms": random.randint(8000, 15000) if is_slow else random.randint(50, 300),
            "status": "ERROR" if is_slow and random.random() < 0.3 else "SUCCESS",
            "db_time_ms": random.randint(7500, 14500) if is_slow else random.randint(30, 150),
            "trace_id": fake.uuid4(),
            "span_id": fake.uuid4()[:16]
        }
        
        if trace["status"] == "ERROR":
            trace["error_message"] = "Connection timeout"
        
        traces.append(trace)
        current += timedelta(seconds=random.randint(15, 45))
    
    save_json(traces, DATA_DIR / "traces" / "scenario1_traces.json")
    
    # 6. Teams Messages
    teams_messages = [
        {
            "@timestamp": format_datetime(today.replace(hour=9, minute=5)),
            "channel": "incident-customerportal",
            "sender": "john.smith@westpac.com",
            "message": "Seeing connection errors in CustomerPortal, investigating now",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=9, minute=15)),
            "channel": "incident-customerportal",
            "sender": "john.smith@westpac.com",
            "message": "This correlates with this morning's deployment - v2.3.1 went live at 08:00",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=9, minute=30)),
            "channel": "incident-customerportal",
            "sender": "sarah.chen@westpac.com",
            "message": "Checking database connection pool metrics now",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=10, minute=0)),
            "channel": "incident-customerportal",
            "sender": "sarah.chen@westpac.com",
            "message": "Found it - new API calls not releasing connections properly. Pool maxed at 50, need ~150",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=10, minute=20)),
            "channel": "incident-customerportal",
            "sender": "john.smith@westpac.com",
            "message": "Preparing emergency change to increase pool size",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=11, minute=10)),
            "channel": "incident-customerportal",
            "sender": "sarah.chen@westpac.com",
            "message": "Resolved - increased pool size to 200 and restarted. Will create PIR this afternoon",
            "thread_id": "thread-001",
            "incident_ref": incident_id
        }
    ]
    save_json(teams_messages, DATA_DIR / "comms" / "scenario1_teams.json")
    
    # 7. Emails
    emails = [
        {
            "@timestamp": format_datetime(today.replace(hour=8, minute=35)),
            "from": "monitoring@westpac.com",
            "to": "oncall-platform@westpac.com",
            "subject": "CRITICAL: CustomerPortal API error rate exceeded",
            "body": "Error rate: 45/min at 08:30 AEDT. Immediate attention required.",
            "incident_ref": incident_id
        },
        {
            "@timestamp": format_datetime(today.replace(hour=9, minute=45)),
            "from": "john.smith@westpac.com",
            "to": "dba-team@westpac.com",
            "subject": "Urgent: Connection pool issues on CustomerPortal DB",
            "body": "Seeing connection pool exhaustion. Need DBA team assistance.",
            "incident_ref": incident_id
        }
    ]
    save_json(emails, DATA_DIR / "comms" / "scenario1_emails.json")
    
    # 8. Knowledge Base Article
    kb_articles = [
        {
            "kb_id": "KB-4783",
            "title": "Database Connection Pool Tuning Guide",
            "content": """# Database Connection Pool Tuning

## Overview
Proper connection pool sizing is critical for application performance.

## Sizing Guidelines
- Base size: 10 connections per application instance
- Max size: (concurrent users / response time) * safety factor
- Typical range: 50-200 connections

## Common Issues
- Pool exhaustion: Increase max size
- Connection leaks: Check code for proper connection release
- Timeout errors: Increase connection timeout

## Monitoring
Monitor pool metrics:
- Active connections
- Idle connections
- Wait time
- Rejection rate

## Resolution Steps
1. Identify connection leak or sizing issue
2. Adjust pool configuration
3. Deploy change
4. Monitor metrics
5. Document in PIR
""",
            "tags": ["database", "performance", "connection-pool"],
            "category": "Infrastructure",
            "last_updated": format_datetime(today - timedelta(days=90)),
            "view_count": 245,
            "helpful_count": 198
        }
    ]
    save_json(kb_articles, DATA_DIR / "knowledge" / "scenario1_kb.json")
    
    console.print("[green]✓ Scenario 1 complete[/green]")
    console.print(f"[dim]Timeline: {change_time.strftime('%I:%M %p')} - {resolution.strftime('%I:%M %p')} today[/dim]")


def main():
    """Main generation function"""
    
    console.print("\n[bold blue]═══════════════════════════════════════════[/bold blue]")
    console.print("[bold blue]  Westpac RCA Demo - Data Generation       [/bold blue]")
    console.print("[bold blue]  UPDATED: Current dates (Feb 4, 2026)     [/bold blue]")
    console.print("[bold blue]═══════════════════════════════════════════[/bold blue]\n")
    
    # Show current time
    now = datetime.now(SYDNEY_TZ)
    console.print(f"[cyan]Current time: {now.strftime('%I:%M %p AEDT, %B %d, %Y')}[/cyan]")
    console.print(f"[cyan]Incident timeline: This morning (08:00-11:00)[/cyan]\n")
    
    # Create data directories
    for subdir in ["incidents", "changes", "problems", "logs", "traces", "comms", "knowledge", "code"]:
        (DATA_DIR / subdir).mkdir(parents=True, exist_ok=True)
    
    # Generate scenarios
    generate_scenario_1()
    
    console.print("\n[bold green]═══════════════════════════════════════════[/bold green]")
    console.print("[bold green]  Data Generation Complete!                [/bold green]")
    console.print("[bold green]═══════════════════════════════════════════[/bold green]\n")
    
    console.print("[bold]Generated data in:[/bold]")
    console.print(f"  {DATA_DIR}\n")
    
    console.print("[bold yellow]⚠️  Data timestamps are from TODAY[/bold yellow]")
    console.print("[yellow]   In Kibana Discover, you can use:[/yellow]")
    console.print("[yellow]   - 'Last 24 hours' (will show today's data)[/yellow]")
    console.print("[yellow]   - Or 'Today' quick select[/yellow]\n")
    
    console.print("[bold]Next step:[/bold]")
    console.print("  python scripts/data_ingestion/ingest_all_data.py\n")


if __name__ == "__main__":
    main()
