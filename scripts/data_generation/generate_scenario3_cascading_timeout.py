"""
Scenario 3: Cascading Timeout Data Generation
Multi-service distributed system failure with temporal correlation

Incident: External payment gateway degradation causes cascading timeouts
Timeline: Feb 3, 2026, 14:00-16:15 (2h 15min)
Services: Payment Service → Inventory Service → OrderProcessing Gateway
Root Cause: Stripe API degradation → cascading timeouts upstream
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random

# Base configuration
BASE_DIR = Path(__file__).parent.parent.parent / "data" / "synthetic" / "scenario3_cascading_timeout"
START_TIME = datetime(2026, 2, 3, 14, 0, 0, tzinfo=timezone.utc)  # Feb 3, 2026 14:00 UTC (1:00 AM Sydney)
DURATION_MINUTES = 135  # 2h 15min incident

# Service definitions
SERVICES = {
    "payment": {
        "app_id": "APP-9123",
        "app_name": "Payment Service",
        "host": "payment-api-prod-02"
    },
    "inventory": {
        "app_id": "APP-5521", 
        "app_name": "Inventory Service",
        "host": "inventory-api-prod-01"
    },
    "order": {
        "app_id": "APP-7654",
        "app_name": "OrderProcessing Gateway",
        "host": "order-gateway-prod-03"
    }
}

# Create output directories
def create_directories():
    """Create directory structure for all data files"""
    dirs = [
        "metrics",
        "logs/app",
        "logs/infra",
        "traces",
        "comms/teams",
        "comms/email",
        "incidents",
        "changes",
        "alerts",
        "knowledge"
    ]
    for dir_path in dirs:
        (BASE_DIR / dir_path).mkdir(parents=True, exist_ok=True)


def get_correlation_id():
    """Generate correlation ID for distributed tracing"""
    return f"corr-{random.randint(100000, 999999)}"


def calculate_payment_response_time(minutes):
    """Calculate Payment Service response time based on timeline"""
    if minutes < 3:  # Before 14:03 - Normal
        return random.uniform(300, 600)
    elif minutes < 20:  # 14:03-14:20 - Degrading
        progress = (minutes - 3) / 17
        return random.uniform(600, 3000) + (progress * 2000)
    elif minutes < 80:  # 14:20-15:20 - Peak degradation
        return random.uniform(3000, 5000)
    elif minutes < 95:  # 15:20-15:35 - Recovering
        progress = (minutes - 80) / 15
        return random.uniform(5000 - (progress * 4000), 1000)
    else:  # After 15:35 - Recovered
        return random.uniform(300, 700)


def calculate_error_rate(service, minutes):
    """Calculate error rate for each service"""
    if service == "payment":
        if minutes < 3:
            return random.uniform(0.1, 0.5)
        elif minutes < 80:
            return random.uniform(5.0, 15.0)
        else:
            return random.uniform(0.5, 2.0)
    
    elif service == "inventory":
        if minutes < 5:
            return random.uniform(0.2, 0.6)
        elif minutes < 80:
            return random.uniform(15.0, 35.0)
        else:
            return random.uniform(1.0, 3.0)
    
    else:  # order
        if minutes < 8:
            return random.uniform(1.0, 3.0)
        elif minutes < 80:
            return random.uniform(30.0, 50.0)
        else:
            return random.uniform(2.0, 5.0)


# ========================================
# METRICS GENERATION
# ========================================

def generate_payment_metrics():
    """Generate Payment Service metrics (250 docs)"""
    print("Generating Payment Service metrics...")
    metrics = []
    
    for minute in range(DURATION_MINUTES):
        timestamp = START_TIME + timedelta(minutes=minute)
        response_time = calculate_payment_response_time(minute)
        error_rate = calculate_error_rate("payment", minute)
        
        # Every 2 minutes
        if minute % 2 == 0:
            metric = {
                "@timestamp": timestamp.isoformat(),
                "app_id": SERVICES["payment"]["app_id"],
                "app_name": SERVICES["payment"]["app_name"],
                "metric_type": "api.response_time",
                "response_time_ms": round(response_time, 2),
                "error_rate_percent": round(error_rate, 2),
                "request_count": random.randint(800, 1200),
                "success_count": random.randint(950, 1180),
                "timeout_count": random.randint(0, 50) if minute > 3 else 0,
                "host": SERVICES["payment"]["host"],
                "environment": "production",
                "service_tier": "api"
            }
            metrics.append(metric)
    
    # Save
    output_file = BASE_DIR / "metrics" / "payment_service_metrics.json"
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Payment metrics: {len(metrics)} documents")
    return len(metrics)


def generate_inventory_metrics():
    """Generate Inventory Service metrics (250 docs)"""
    print("Generating Inventory Service metrics...")
    metrics = []
    
    for minute in range(DURATION_MINUTES):
        timestamp = START_TIME + timedelta(minutes=minute)
        
        # Inventory affected after Payment starts degrading
        if minute < 5:
            response_time = random.uniform(100, 300)
            timeout_rate = random.uniform(0.1, 0.5)
        elif minute < 80:
            response_time = random.uniform(4000, 6000)  # Waiting for payment
            timeout_rate = random.uniform(20.0, 40.0)
        else:
            response_time = random.uniform(150, 400)
            timeout_rate = random.uniform(0.5, 2.0)
        
        if minute % 2 == 0:
            metric = {
                "@timestamp": timestamp.isoformat(),
                "app_id": SERVICES["inventory"]["app_id"],
                "app_name": SERVICES["inventory"]["app_name"],
                "metric_type": "api.response_time",
                "response_time_ms": round(response_time, 2),
                "timeout_rate_percent": round(timeout_rate, 2),
                "request_count": random.randint(600, 900),
                "timeout_count": int(random.randint(600, 900) * timeout_rate / 100),
                "host": SERVICES["inventory"]["host"],
                "environment": "production",
                "dependency": "payment-service"
            }
            metrics.append(metric)
    
    output_file = BASE_DIR / "metrics" / "inventory_service_metrics.json"
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ Inventory metrics: {len(metrics)} documents")
    return len(metrics)


def generate_order_metrics():
    """Generate OrderProcessing Gateway metrics (300 docs)"""
    print("Generating OrderProcessing Gateway metrics...")
    metrics = []
    
    for minute in range(DURATION_MINUTES):
        timestamp = START_TIME + timedelta(minutes=minute)
        error_rate = calculate_error_rate("order", minute)
        
        # Order gateway affected after Inventory starts failing
        if minute < 8:
            response_time = random.uniform(200, 500)
            success_rate = random.uniform(97.0, 99.5)
        elif minute < 80:
            response_time = random.uniform(8000, 12000)
            success_rate = random.uniform(50.0, 70.0)
        else:
            response_time = random.uniform(300, 600)
            success_rate = random.uniform(95.0, 98.0)
        
        if minute % 1 == 0:  # Every minute for order gateway
            metric = {
                "@timestamp": timestamp.isoformat(),
                "app_id": SERVICES["order"]["app_id"],
                "app_name": SERVICES["order"]["app_name"],
                "metric_type": "gateway.performance",
                "response_time_ms": round(response_time, 2),
                "error_rate_percent": round(error_rate, 2),
                "success_rate_percent": round(success_rate, 2),
                "request_count": random.randint(1000, 1500),
                "failed_orders": int(random.randint(1000, 1500) * error_rate / 100),
                "host": SERVICES["order"]["host"],
                "environment": "production",
                "endpoint": "/api/v1/orders"
            }
            metrics.append(metric)
    
    output_file = BASE_DIR / "metrics" / "order_gateway_metrics.json"
    with open(output_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"✓ OrderProcessing metrics: {len(metrics)} documents")
    return len(metrics)


# ========================================
# LOGS GENERATION
# ========================================

def generate_payment_logs():
    """Generate Payment Service application logs"""
    print("Generating Payment Service logs...")
    logs = []
    
    # Key events timeline
    events = [
        (3, "WARN", "Stripe API response time increased to 2500ms"),
        (5, "WARN", "Stripe API response time: 3200ms (threshold: 1000ms)"),
        (10, "ERROR", "Stripe API timeout after 5000ms - order payment failed"),
        (15, "ERROR", "High rate of Stripe API timeouts detected: 15%"),
        (20, "CRITICAL", "Stripe API degraded - timeout rate: 25%"),
        (45, "ERROR", "Stripe payment gateway responding slowly (4800ms avg)"),
        (60, "CRITICAL", "External dependency failure - Stripe API"),
        (80, "INFO", "Switched to backup payment gateway (Adyen)"),
        (85, "INFO", "Payment processing stabilizing on backup gateway"),
        (95, "INFO", "Stripe API recovered - switching back to primary"),
    ]
    
    for minute_offset, level, message in events:
        timestamp = START_TIME + timedelta(minutes=minute_offset)
        log = {
            "@timestamp": timestamp.isoformat(),
            "app_id": SERVICES["payment"]["app_id"],
            "app_name": SERVICES["payment"]["app_name"],
            "level": level,
            "message": message,
            "host": SERVICES["payment"]["host"],
            "environment": "production",
            "logger": "com.westpac.payment.gateway.StripeClient"
        }
        logs.append(log)
    
    output_file = BASE_DIR / "logs" / "app" / "payment_service_logs.json"
    with open(output_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"✓ Payment logs: {len(logs)} documents")
    return len(logs)


def generate_inventory_logs():
    """Generate Inventory Service application logs"""
    print("Generating Inventory Service logs...")
    logs = []
    
    events = [
        (5, "WARN", "Payment service response time exceeded 3000ms"),
        (8, "ERROR", "Timeout calling payment-service: Connection timeout after 5000ms"),
        (12, "ERROR", "Payment verification failed - timeout waiting for payment-service"),
        (18, "CRITICAL", "High timeout rate calling payment-service: 30%"),
        (25, "ERROR", "Unable to verify payment status - payment-service unavailable"),
        (40, "CRITICAL", "Cascading failure - payment-service timeouts causing inventory holds"),
        (75, "INFO", "Payment service response improving"),
        (90, "INFO", "Payment service integration stabilized"),
    ]
    
    for minute_offset, level, message in events:
        timestamp = START_TIME + timedelta(minutes=minute_offset)
        log = {
            "@timestamp": timestamp.isoformat(),
            "app_id": SERVICES["inventory"]["app_id"],
            "app_name": SERVICES["inventory"]["app_name"],
            "level": level,
            "message": message,
            "host": SERVICES["inventory"]["host"],
            "environment": "production",
            "logger": "com.westpac.inventory.service.PaymentIntegration"
        }
        logs.append(log)
    
    output_file = BASE_DIR / "logs" / "app" / "inventory_service_logs.json"
    with open(output_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"✓ Inventory logs: {len(logs)} documents")
    return len(logs)


def generate_order_logs():
    """Generate OrderProcessing Gateway application logs"""
    print("Generating OrderProcessing Gateway logs...")
    logs = []
    
    events = [
        (8, "WARN", "Order processing slowing - inventory-service delays"),
        (10, "ERROR", "Order creation failed - inventory-service timeout"),
        (12, "ERROR", "HTTP 504 Gateway Timeout from inventory-service"),
        (15, "CRITICAL", "Order failure rate spiking - 45% failed"),
        (20, "CRITICAL", "Customer impact - orders failing due to downstream timeouts"),
        (30, "ERROR", "Cascading timeout - inventory-service → payment-service"),
        (45, "CRITICAL", "Critical: 50% order failure rate"),
        (60, "ERROR", "Multiple downstream service failures detected"),
        (80, "INFO", "Downstream services recovering"),
        (95, "INFO", "Order processing normalized"),
    ]
    
    for minute_offset, level, message in events:
        timestamp = START_TIME + timedelta(minutes=minute_offset)
        log = {
            "@timestamp": timestamp.isoformat(),
            "app_id": SERVICES["order"]["app_id"],
            "app_name": SERVICES["order"]["app_name"],
            "level": level,
            "message": message,
            "host": SERVICES["order"]["host"],
            "environment": "production",
            "logger": "com.westpac.order.gateway.OrderController"
        }
        logs.append(log)
    
    output_file = BASE_DIR / "logs" / "app" / "order_gateway_logs.json"
    with open(output_file, 'w') as f:
        json.dump(logs, f, indent=2)
    
    print(f"✓ OrderProcessing logs: {len(logs)} documents")
    return len(logs)


# ========================================
# DISTRIBUTED TRACES
# ========================================

def generate_distributed_traces():
    """Generate APM traces showing cascading failure"""
    print("Generating distributed traces...")
    traces = []
    
    # Generate traces every 5 minutes
    for minute in range(0, DURATION_MINUTES, 5):
        timestamp = START_TIME + timedelta(minutes=minute)
        corr_id = get_correlation_id()
        
        payment_time = calculate_payment_response_time(minute)
        
        # Full trace: Order → Inventory → Payment → Stripe
        trace = {
            "@timestamp": timestamp.isoformat(),
            "trace_id": corr_id,
            "service_chain": [
                {
                    "service": "order-gateway",
                    "app_id": SERVICES["order"]["app_id"],
                    "duration_ms": payment_time + 500,
                    "status": "error" if minute > 8 and minute < 80 else "success"
                },
                {
                    "service": "inventory-service",
                    "app_id": SERVICES["inventory"]["app_id"],
                    "duration_ms": payment_time + 300,
                    "status": "error" if minute > 5 and minute < 80 else "success"
                },
                {
                    "service": "payment-service",
                    "app_id": SERVICES["payment"]["app_id"],
                    "duration_ms": payment_time,
                    "status": "error" if minute > 3 and minute < 80 else "success"
                },
                {
                    "service": "stripe-api",
                    "app_id": "external",
                    "duration_ms": payment_time - 100,
                    "status": "error" if minute > 3 and minute < 80 else "success",
                    "external": True
                }
            ],
            "total_duration_ms": payment_time + 500,
            "success": minute < 8 or minute > 80,
            "environment": "production"
        }
        traces.append(trace)
    
    output_file = BASE_DIR / "traces" / "distributed_traces.json"
    with open(output_file, 'w') as f:
        json.dump(traces, f, indent=2)
    
    print(f"✓ Distributed traces: {len(traces)} documents")
    return len(traces)


# ========================================
# COMMUNICATIONS
# ========================================

def generate_communications():
    """Generate Teams/email communications"""
    print("Generating communications...")
    
    teams_messages = [
        {
            "@timestamp": (START_TIME + timedelta(minutes=15)).isoformat(),
            "channel": "platform-alerts",
            "author": "AlertBot",
            "message": "🚨 ALERT: High error rate on OrderProcessing Gateway (APP-7654) - 45% failure rate",
            "app_id": SERVICES["order"]["app_id"],
            "channel_type": "teams",
            "incident_ref": "INC0034567"
        },
        {
            "@timestamp": (START_TIME + timedelta(minutes=20)).isoformat(),
            "channel": "platform-oncall",
            "author": "Sarah Chen",
            "message": "Looking at order-gateway logs - seeing lots of 504 timeouts from inventory-service",
            "app_id": SERVICES["order"]["app_id"],
            "channel_type": "teams"
        },
        {
            "@timestamp": (START_TIME + timedelta(minutes=45)).isoformat(),
            "channel": "platform-oncall",
            "author": "Mike Rodriguez",
            "message": "Checked inventory-service - it's timing out on payment-service calls. Root cause might be upstream",
            "app_id": SERVICES["inventory"]["app_id"],
            "channel_type": "teams"
        },
        {
            "@timestamp": (START_TIME + timedelta(minutes=75)).isoformat(),
            "channel": "platform-oncall",
            "author": "Sarah Chen",
            "message": "FOUND IT! Payment-service is slow because Stripe API is degraded. Switching to Adyen backup gateway.",
            "app_id": SERVICES["payment"]["app_id"],
            "channel_type": "teams"
        },
        {
            "@timestamp": (START_TIME + timedelta(minutes=90)).isoformat(),
            "channel": "platform-alerts",
            "author": "AlertBot",
            "message": "✅ RESOLVED: Order processing gateway error rate back to normal",
            "app_id": SERVICES["order"]["app_id"],
            "channel_type": "teams",
            "incident_ref": "INC0034567"
        }
    ]
    
    output_file = BASE_DIR / "comms" / "teams" / "teams_messages.json"
    with open(output_file, 'w') as f:
        json.dump(teams_messages, f, indent=2)
    
    print(f"✓ Teams messages: {len(teams_messages)} documents")
    return len(teams_messages)


# ========================================
# INCIDENTS & ALERTS
# ========================================

def generate_incident():
    """Generate incident record"""
    print("Generating incident record...")
    
    incident = {
        "@timestamp": (START_TIME + timedelta(minutes=15)).isoformat(),
        "incident_id": "INC0034567",
        "app_id": SERVICES["order"]["app_id"],
        "app_name": SERVICES["order"]["app_name"],
        "title": "High Order Failure Rate - OrderProcessing Gateway",
        "description": "Customer orders failing with 45% error rate. Order gateway showing HTTP 504 timeouts.",
        "severity": "P1",
        "status": "resolved",
        "detected_at": (START_TIME + timedelta(minutes=15)).isoformat(),
        "resolved_at": (START_TIME + timedelta(minutes=95)).isoformat(),
        "duration_minutes": 80,
        "reported_by": "monitoring-system",
        "assigned_to": "platform-engineering",
        "root_cause_summary": "External payment gateway (Stripe) degradation caused cascading timeouts through inventory-service to order-gateway",
        "resolution": "Switched to backup payment gateway (Adyen) while Stripe recovered",
        "customer_impact": "High - 45% order failure rate for 70 minutes",
        "services_affected": ["order-gateway", "inventory-service", "payment-service"]
    }
    
    output_file = BASE_DIR / "incidents" / "incident.json"
    with open(output_file, 'w') as f:
        json.dump([incident], f, indent=2)
    
    print(f"✓ Incident record: 1 document")
    return 1


def generate_alerts():
    """Generate alert records"""
    print("Generating alerts...")
    
    alerts = [
        {
            "@timestamp": (START_TIME + timedelta(minutes=15)).isoformat(),
            "alert_id": "ALT-TIMEOUT-001",
            "alert_name": "High Error Rate - OrderProcessing Gateway",
            "app_id": SERVICES["order"]["app_id"],
            "alert_timestamp": (START_TIME + timedelta(minutes=15)).isoformat(),
            "threshold_value": 45.0,
            "threshold_config": 10.0,
            "alert_status": "fired",
            "severity": "critical",
            "incident_created": "yes",
            "incident_ref": "INC0034567"
        },
        {
            "@timestamp": (START_TIME + timedelta(minutes=95)).isoformat(),
            "alert_id": "ALT-TIMEOUT-001",
            "alert_name": "High Error Rate - OrderProcessing Gateway",
            "app_id": SERVICES["order"]["app_id"],
            "alert_timestamp": (START_TIME + timedelta(minutes=95)).isoformat(),
            "threshold_value": 3.2,
            "threshold_config": 10.0,
            "alert_status": "resolved",
            "severity": "info",
            "incident_ref": "INC0034567"
        }
    ]
    
    output_file = BASE_DIR / "alerts" / "alerts.json"
    with open(output_file, 'w') as f:
        json.dump(alerts, f, indent=2)
    
    print(f"✓ Alerts: {len(alerts)} documents")
    return len(alerts)


def generate_knowledge_base():
    """Generate knowledge base entry"""
    print("Generating knowledge base article...")
    
    kb = {
        "@timestamp": (START_TIME + timedelta(minutes=120)).isoformat(),
        "kb_id": "KB-CASCADE-001",
        "title": "Troubleshooting Cascading Timeouts in Distributed Systems",
        "category": "distributed-systems",
        "tags": ["timeout", "cascading-failure", "distributed-tracing", "dependencies"],
        "summary": "Guide for diagnosing cascading timeout failures across microservices",
        "symptoms": [
            "Downstream services showing high error rates",
            "HTTP 504 Gateway Timeout errors",
            "Service response times exceeding timeout thresholds",
            "Error propagation across service boundaries"
        ],
        "diagnosis_steps": [
            "Check distributed traces to identify slowest service in chain",
            "Look for timeout errors in application logs",
            "Verify external dependency health (payment gateways, APIs)",
            "Trace request path backwards from error to origin",
            "Check for recent changes in upstream services"
        ],
        "common_causes": [
            "External API degradation or outages",
            "Database connection pool exhaustion",
            "Network latency spikes",
            "Upstream service deployment issues",
            "Resource contention (CPU, memory, threads)"
        ],
        "resolution_patterns": [
            "Switch to backup service/gateway if available",
            "Increase timeout thresholds temporarily",
            "Enable circuit breakers to prevent cascading failures",
            "Scale affected services horizontally",
            "Implement retry logic with exponential backoff"
        ],
        "related_incidents": ["INC0034567"],
        "created_by": "platform-engineering",
        "last_updated": (START_TIME + timedelta(days=1)).isoformat()
    }
    
    output_file = BASE_DIR / "knowledge" / "kb_cascading_timeouts.json"
    with open(output_file, 'w') as f:
        json.dump([kb], f, indent=2)
    
    print(f"✓ Knowledge base: 1 document")
    return 1


# ========================================
# MAIN EXECUTION
# ========================================

def main():
    """Generate all Scenario 3 data"""
    print("=" * 70)
    print("SCENARIO 3: CASCADING TIMEOUT DATA GENERATION")
    print("=" * 70)
    print(f"Incident: INC0034567")
    print(f"Timeline: Feb 3, 2026, 14:00-16:15 UTC")
    print(f"Duration: 2 hours 15 minutes")
    print(f"Services: 3 (Payment, Inventory, OrderProcessing)")
    print("=" * 70)
    print()
    
    # Create directories
    print("Creating directory structure...")
    create_directories()
    print()
    
    # Generate all data
    total_docs = 0
    
    print("Generating metrics...")
    total_docs += generate_payment_metrics()
    total_docs += generate_inventory_metrics()
    total_docs += generate_order_metrics()
    print()
    
    print("Generating logs...")
    total_docs += generate_payment_logs()
    total_docs += generate_inventory_logs()
    total_docs += generate_order_logs()
    print()
    
    print("Generating traces...")
    total_docs += generate_distributed_traces()
    print()
    
    print("Generating communications...")
    total_docs += generate_communications()
    print()
    
    print("Generating incidents & alerts...")
    total_docs += generate_incident()
    total_docs += generate_alerts()
    print()
    
    print("Generating knowledge base...")
    total_docs += generate_knowledge_base()
    print()
    
    # Summary
    print("=" * 70)
    print(f"✅ DATA GENERATION COMPLETE: {total_docs} documents")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Run ingestion script:")
    print("   python scripts/data_ingestion/ingest_scenario3_data.py")
    print()
    print("2. Verify in Kibana Discover:")
    print("   Search: incident_id:\"INC0034567\"")
    print("   Time range: Feb 3, 2026, 14:00-16:30")
    print("   Expected: ~950 documents")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
