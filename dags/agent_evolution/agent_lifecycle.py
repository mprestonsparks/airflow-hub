"""
DEAN Agent Lifecycle DAG
Manages agent creation, evolution, and retirement per specifications.
REAL IMPLEMENTATION - NO MOCKS
"""

from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, Any
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.exceptions import AirflowException

# Configure logging
logger = logging.getLogger(__name__)

# DEAN API endpoint configuration
DEAN_API_URL = "http://dean-api:8091/api/v1"
API_TIMEOUT = 30

default_args = {
    'owner': 'agent-evolution',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'dean_agent_lifecycle',
    default_args=default_args,
    description='Manages DEAN agent creation, evolution, and retirement',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    catchup=False,
    tags=['dean', 'agent-evolution', 'automated']
)

def check_global_budget(**context) -> Dict[str, Any]:
    """Check if global token budget allows new agents via REAL API."""
    try:
        # Get system metrics to check token budget
        response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        metrics = response.json()
        
        tokens_data = metrics.get('tokens', {})
        allocated = tokens_data.get('allocated', 0)
        consumed = tokens_data.get('consumed', 0)
        
        # Default global budget: 1M tokens
        global_budget = context['params'].get('global_token_budget', 1000000)
        remaining = global_budget - allocated
        
        # Need at least 10k tokens to spawn new agents
        budget_available = remaining >= 10000
        
        logger.info(f"Token budget check: allocated={allocated}, consumed={consumed}, remaining={remaining}")
        
        return {
            "budget_available": budget_available,
            "remaining_tokens": remaining,
            "allocated_tokens": allocated,
            "consumed_tokens": consumed
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to check token budget: {e}")
        raise AirflowException(f"API call failed: {e}")

def spawn_agents(**context) -> Dict[str, Any]:
    """Spawn new agents with economic constraints via REAL API."""
    try:
        # Get parameters
        agent_count = context['params'].get('agent_count', 3)
        token_budget_per_agent = context['params'].get('token_budget', 4096)
        
        # Check if we should spawn agents
        ti = context['ti']
        budget_check = ti.xcom_pull(task_ids='check_token_budget')
        
        if not budget_check.get('budget_available'):
            logger.warning("Insufficient token budget - skipping agent spawn")
            return {"agents_spawned": 0, "total_tokens_allocated": 0}
        
        agents_created = []
        total_tokens = 0
        
        # Spawn each agent
        for i in range(agent_count):
            response = requests.post(
                f"{DEAN_API_URL}/agents",
                json={
                    "goal": f"Optimize codebase performance (batch {context['ds']})",
                    "token_budget": token_budget_per_agent,
                    "diversity_weight": 0.5,
                    "specialized_domain": "performance_optimization"
                },
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                agents_created.append(agent_data['id'])
                total_tokens += agent_data['token_budget']
                logger.info(f"Created agent {agent_data['id']} with {agent_data['token_budget']} tokens")
            else:
                logger.error(f"Failed to create agent {i+1}: {response.text}")
        
        return {
            "agents_spawned": len(agents_created),
            "agent_ids": agents_created,
            "total_tokens_allocated": total_tokens
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to spawn agents: {e}")
        raise AirflowException(f"API call failed: {e}")

def evolve_population(**context) -> Dict[str, Any]:
    """Evolve the agent population via REAL API."""
    try:
        # Get parameters
        evolution_cycles = context['params'].get('evolution_cycles', 1)
        parallel_workers = context['params'].get('parallel_workers', 4)
        
        # Get spawned agents from previous task
        ti = context['ti']
        spawn_result = ti.xcom_pull(task_ids='spawn_agents')
        
        # Evolve entire population
        response = requests.post(
            f"{DEAN_API_URL}/population/evolve",
            json={
                "cycles": evolution_cycles,
                "parallel_workers": parallel_workers
            },
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        evolution_result = response.json()
        
        # Get diversity metrics
        diversity_response = requests.get(
            f"{DEAN_API_URL}/system/diversity",
            timeout=API_TIMEOUT
        )
        diversity_data = diversity_response.json() if diversity_response.status_code == 200 else {}
        
        logger.info(f"Population evolution completed: {evolution_result}")
        
        return {
            "evolution_cycles": evolution_result.get('cycles', evolution_cycles),
            "diversity_score": diversity_data.get('diversity_score', 0.0),
            "agent_count": diversity_data.get('agent_count', 0),
            "requires_intervention": diversity_data.get('requires_intervention', False)
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to evolve population: {e}")
        raise AirflowException(f"API call failed: {e}")

# Define tasks with parameters
check_budget_task = PythonOperator(
    task_id='check_token_budget',
    python_callable=check_global_budget,
    params={
        'global_token_budget': 1000000  # 1M tokens
    },
    dag=dag
)

spawn_agents_task = PythonOperator(
    task_id='spawn_agents',
    python_callable=spawn_agents,
    params={
        'agent_count': 3,
        'token_budget': 4096
    },
    dag=dag
)

evolve_population_task = PythonOperator(
    task_id='evolve_population',
    python_callable=evolve_population,
    params={
        'evolution_cycles': 1,
        'parallel_workers': 4
    },
    dag=dag
)

# Add task to check and retire exhausted agents
def retire_exhausted_agents(**context) -> Dict[str, Any]:
    """Retire agents that have exhausted their token budget."""
    try:
        # Get all active agents
        response = requests.get(
            f"{DEAN_API_URL}/agents?active_only=true",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        agents_data = response.json()
        agents = agents_data.get('agents', [])
        
        retired_count = 0
        
        for agent in agents:
            # Check if agent has exhausted budget (90% consumed)
            if agent['tokens_consumed'] >= agent['token_budget'] * 0.9:
                # Update agent status to completed
                retire_response = requests.patch(
                    f"{DEAN_API_URL}/agents/{agent['id']}",
                    json={"status": "completed"},
                    timeout=API_TIMEOUT
                )
                
                if retire_response.status_code == 200:
                    retired_count += 1
                    logger.info(f"Retired agent {agent['id']} - tokens exhausted")
        
        return {
            "agents_retired": retired_count,
            "active_agents_remaining": len(agents) - retired_count
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retire agents: {e}")
        raise AirflowException(f"API call failed: {e}")

retire_agents_task = PythonOperator(
    task_id='retire_exhausted_agents',
    python_callable=retire_exhausted_agents,
    dag=dag
)

# Set dependencies
check_budget_task >> spawn_agents_task >> evolve_population_task >> retire_agents_task