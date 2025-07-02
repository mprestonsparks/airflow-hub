#!/usr/bin/env python3
"""
DEAN Evolution DAG - Orchestrates agent evolution cycles
Manages the complete evolution workflow with monitoring and error handling
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import json
import logging

# Configuration
DEAN_ORCHESTRATOR_URL = Variable.get("dean_orchestrator_url", "http://dean-orchestrator:8082")
INDEXAGENT_URL = Variable.get("indexagent_url", "http://indexagent:8081")
EVOLUTION_API_URL = Variable.get("evolution_api_url", "http://dean-api:8091")

# Default DAG arguments
default_args = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 25),
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['dean-alerts@example.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

# Create DAG
dag = DAG(
    'dean_evolution_cycle',
    default_args=default_args,
    description='Orchestrates DEAN agent evolution cycles',
    schedule_interval='*/30 * * * *',  # Every 30 minutes
    catchup=False,
    tags=['dean', 'evolution', 'agents'],
)

def check_system_health(**context):
    """Check overall system health before evolution."""
    import requests
    
    services = {
        'DEAN Orchestrator': f"{DEAN_ORCHESTRATOR_URL}/health",
        'IndexAgent': f"{INDEXAGENT_URL}/health",
        'Evolution API': f"{EVOLUTION_API_URL}/health"
    }
    
    all_healthy = True
    health_status = {}
    
    for service_name, health_url in services.items():
        try:
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                health_status[service_name] = health_data.get('status', 'unknown')
                if health_data.get('status') != 'healthy':
                    all_healthy = False
            else:
                health_status[service_name] = 'unhealthy'
                all_healthy = False
        except Exception as e:
            logging.error(f"Failed to check {service_name}: {str(e)}")
            health_status[service_name] = 'unreachable'
            all_healthy = False
    
    # Push health status to XCom
    context['task_instance'].xcom_push(key='health_status', value=health_status)
    
    if not all_healthy:
        raise ValueError(f"System health check failed: {health_status}")
    
    logging.info(f"All services healthy: {health_status}")
    return health_status

def get_evolution_candidates(**context):
    """Get agents eligible for evolution."""
    import requests
    
    # Get all active agents
    response = requests.get(f"{INDEXAGENT_URL}/api/v1/agents")
    agents = response.json().get('agents', [])
    
    # Filter candidates based on criteria
    candidates = []
    for agent in agents:
        if agent.get('status') == 'active':
            # Check eligibility criteria
            if agent.get('generation', 0) < 100:  # Max 100 generations
                if agent.get('token_budget', {}).get('remaining', 0) > 1000:  # Has budget
                    candidates.append(agent['id'])
    
    logging.info(f"Found {len(candidates)} evolution candidates")
    
    # Push to XCom
    context['task_instance'].xcom_push(key='evolution_candidates', value=candidates)
    
    return candidates

def check_diversity_threshold(**context):
    """Check population diversity and trigger interventions if needed."""
    import requests
    
    candidates = context['task_instance'].xcom_pull(key='evolution_candidates')
    
    if len(candidates) < 2:
        logging.info("Too few candidates for diversity check")
        return {'diversity_ok': True, 'score': 1.0}
    
    # Check population diversity
    response = requests.post(
        f"{INDEXAGENT_URL}/api/v1/diversity/population",
        json={'population_ids': candidates[:20]}  # Check first 20
    )
    
    diversity_data = response.json()
    diversity_score = diversity_data.get('diversity_score', 0)
    
    result = {
        'diversity_ok': diversity_score >= 0.3,
        'score': diversity_score,
        'intervention_needed': diversity_score < 0.3
    }
    
    context['task_instance'].xcom_push(key='diversity_check', value=result)
    
    if not result['diversity_ok']:
        logging.warning(f"Low diversity detected: {diversity_score}")
    
    return result

def orchestrate_evolution(**context):
    """Orchestrate the main evolution cycle."""
    import requests
    
    candidates = context['task_instance'].xcom_pull(key='evolution_candidates')
    diversity_check = context['task_instance'].xcom_pull(key='diversity_check')
    
    if not candidates:
        logging.info("No candidates for evolution")
        return {'status': 'no_candidates'}
    
    # Prepare evolution request
    evolution_params = {
        'population_ids': candidates[:10],  # Evolve up to 10 agents
        'generations': 5,
        'token_budget': 10000,
        'ca_rules': [110, 30, 90, 184],
        'diversity_threshold': 0.3,
        'pattern_sharing': True
    }
    
    # Call orchestrator
    response = requests.post(
        f"{DEAN_ORCHESTRATOR_URL}/api/v1/evolution/orchestrate",
        json=evolution_params
    )
    
    if response.status_code == 200:
        result = response.json()
        logging.info(f"Evolution orchestrated: {result}")
        
        # Push result to XCom
        context['task_instance'].xcom_push(key='evolution_result', value=result)
        
        return result
    else:
        raise ValueError(f"Evolution failed: {response.text}")

def collect_evolution_metrics(**context):
    """Collect and store evolution metrics."""
    import requests
    
    evolution_result = context['task_instance'].xcom_pull(key='evolution_result')
    
    if not evolution_result:
        return {'status': 'no_evolution_data'}
    
    # Get population status
    response = requests.get(f"{DEAN_ORCHESTRATOR_URL}/api/v1/population/status")
    population_status = response.json()
    
    # Collect metrics
    metrics = {
        'timestamp': datetime.utcnow().isoformat(),
        'evolution_cycle_id': evolution_result.get('cycle_id'),
        'agents_evolved': evolution_result.get('population_size', 0),
        'initial_diversity': evolution_result.get('initial_diversity', 0),
        'total_agents': population_status.get('total_agents', 0),
        'active_agents': population_status.get('active_agents', 0),
        'average_fitness': population_status.get('average_fitness', 0),
        'population_diversity': population_status.get('population_diversity', 0),
        'patterns_discovered': len(population_status.get('discovered_patterns', [])),
        'token_usage': population_status.get('token_usage', {})
    }
    
    # Log metrics
    logging.info(f"Evolution metrics: {json.dumps(metrics, indent=2)}")
    
    # Push to monitoring system (placeholder)
    # In production, this would send to Prometheus/Grafana
    context['task_instance'].xcom_push(key='evolution_metrics', value=metrics)
    
    return metrics

def notify_evolution_complete(**context):
    """Send notifications about evolution completion."""
    metrics = context['task_instance'].xcom_pull(key='evolution_metrics')
    
    if not metrics:
        return
    
    # Format notification
    message = f"""
    DEAN Evolution Cycle Complete
    
    Cycle ID: {metrics.get('evolution_cycle_id', 'unknown')}
    Agents Evolved: {metrics.get('agents_evolved', 0)}
    Population Diversity: {metrics.get('population_diversity', 0):.3f}
    Average Fitness: {metrics.get('average_fitness', 0):.3f}
    Patterns Discovered: {metrics.get('patterns_discovered', 0)}
    
    Token Usage:
    - Allocated: {metrics.get('token_usage', {}).get('allocated', 0)}
    - Consumed: {metrics.get('token_usage', {}).get('consumed', 0)}
    - Available: {metrics.get('token_usage', {}).get('available', 0)}
    """
    
    logging.info(message)
    
    # In production, this would send to Slack/email/etc
    return {'notification_sent': True}

# Define tasks
with dag:
    # Health check
    health_check = PythonOperator(
        task_id='check_system_health',
        python_callable=check_system_health,
        provide_context=True,
    )
    
    # Get candidates
    get_candidates = PythonOperator(
        task_id='get_evolution_candidates',
        python_callable=get_evolution_candidates,
        provide_context=True,
    )
    
    # Diversity check
    diversity_check = PythonOperator(
        task_id='check_diversity_threshold',
        python_callable=check_diversity_threshold,
        provide_context=True,
    )
    
    # Main evolution
    evolution = PythonOperator(
        task_id='orchestrate_evolution',
        python_callable=orchestrate_evolution,
        provide_context=True,
    )
    
    # Collect metrics
    metrics = PythonOperator(
        task_id='collect_evolution_metrics',
        python_callable=collect_evolution_metrics,
        provide_context=True,
    )
    
    # Notification
    notify = PythonOperator(
        task_id='notify_evolution_complete',
        python_callable=notify_evolution_complete,
        provide_context=True,
        trigger_rule='none_failed_or_skipped',
    )
    
    # Set dependencies
    health_check >> get_candidates >> diversity_check >> evolution >> metrics >> notify