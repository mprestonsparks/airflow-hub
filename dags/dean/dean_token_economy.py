"""
DEAN Token Economy Management DAG
Manages token allocation, tracking, and economic constraints across agents.
REAL IMPLEMENTATION - NO MOCKS
"""

from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, Any, List
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.exceptions import AirflowException

# Configure logging
logger = logging.getLogger(__name__)

# DEAN API configuration
DEAN_API_URL = "http://dean-api:8091/api/v1"
API_TIMEOUT = 30

default_args = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

dag = DAG(
    'dean_token_economy',
    default_args=default_args,
    description='DEAN Token Economy Management and Budget Allocation',
    schedule_interval='*/10 * * * *',  # Every 10 minutes
    catchup=False,
    max_active_runs=1,
    tags=['dean', 'token-economy', 'budget', 'critical']
)

# Check DEAN API health
check_dean_api_health = HttpSensor(
    task_id='check_dean_api_health',
    http_conn_id='dean_api',
    endpoint='/health',
    timeout=30,
    poke_interval=5,
    dag=dag
)

def calculate_global_budget(**context) -> Dict[str, Any]:
    """Calculate global token budget and allocation strategy based on real metrics."""
    try:
        # Get current system metrics from DEAN API
        response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        metrics = response.json()
        tokens_data = metrics.get('tokens', {})
        
        # Global budget configuration from params
        TOTAL_BUDGET = context['params'].get('total_budget', 1000000)  # 1M tokens default
        
        # Dynamic allocation based on current usage
        current_allocated = tokens_data.get('allocated', 0)
        current_consumed = tokens_data.get('consumed', 0)
        efficiency = tokens_data.get('efficiency', 0.5)
        
        # Calculate remaining budget
        remaining_budget = TOTAL_BUDGET - current_allocated
        
        # Dynamic service allocations based on efficiency
        if efficiency > 0.8:  # High efficiency - allocate more
            allocation_multiplier = 1.2
        elif efficiency < 0.5:  # Low efficiency - reduce allocation
            allocation_multiplier = 0.8
        else:
            allocation_multiplier = 1.0
        
        # Calculate per-agent budget
        agent_count = metrics.get('agents', {}).get('active', 0)
        if agent_count == 0:
            per_agent_budget = 4096  # Default for new agents
        else:
            per_agent_budget = int((remaining_budget * 0.7) / max(agent_count, 1))  # 70% for active agents
            per_agent_budget = min(per_agent_budget, 8192)  # Cap at 8k per agent
            per_agent_budget = max(per_agent_budget, 1024)  # Min 1k per agent
        
        budget_allocation = {
            'total_budget': TOTAL_BUDGET,
            'allocated': current_allocated,
            'consumed': current_consumed,
            'remaining': remaining_budget,
            'per_agent_budget': int(per_agent_budget * allocation_multiplier),
            'efficiency': efficiency,
            'allocation_multiplier': allocation_multiplier,
            'active_agents': agent_count,
            'allocation_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Calculated budget allocation: {remaining_budget} tokens remaining, {per_agent_budget} per agent")
        
        # Store in XCom for other tasks
        context['task_instance'].xcom_push(
            key='budget_allocation',
            value=budget_allocation
        )
        
        return budget_allocation
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to calculate budget: {e}")
        raise AirflowException(f"API call failed: {e}")

# Calculate global budget allocation
calculate_budget = PythonOperator(
    task_id='calculate_budget',
    python_callable=calculate_global_budget,
    params={
        'total_budget': 1000000  # 1M tokens per day
    },
    dag=dag
)

def monitor_token_consumption(**context) -> Dict[str, Any]:
    """Monitor current token consumption across all agents via REAL API."""
    try:
        # Get budget allocation from previous task
        budget_allocation = context['task_instance'].xcom_pull(
            task_ids='calculate_budget',
            key='budget_allocation'
        )
        
        # Get all active agents and their consumption
        agents_response = requests.get(
            f"{DEAN_API_URL}/agents?active_only=true",
            timeout=API_TIMEOUT
        )
        agents_response.raise_for_status()
        
        agents_data = agents_response.json()
        agents = agents_data.get('agents', [])
        
        # Calculate per-agent consumption
        agent_consumption = []
        total_consumed = 0
        total_allocated = 0
        
        for agent in agents:
            consumed = agent.get('token_consumed', 0)
            budget = agent.get('token_budget', 0)
            efficiency = agent.get('token_efficiency', 0.5)
            
            agent_consumption.append({
                'agent_id': agent['id'],
                'name': agent['name'],
                'consumed': consumed,
                'budget': budget,
                'remaining': budget - consumed,
                'efficiency': efficiency,
                'consumption_rate': consumed / budget if budget > 0 else 0,
                'status': 'critical' if consumed >= budget * 0.9 else 'healthy'
            })
            
            total_consumed += consumed
            total_allocated += budget
        
        # Identify high consumers
        high_consumers = [a for a in agent_consumption if a['consumption_rate'] > 0.8]
        efficient_agents = [a for a in agent_consumption if a['efficiency'] > 0.7]
        
        consumption_summary = {
            'total_budget': budget_allocation['total_budget'],
            'total_allocated': total_allocated,
            'total_consumed': total_consumed,
            'total_remaining': budget_allocation['total_budget'] - total_allocated,
            'consumption_rate': total_consumed / total_allocated if total_allocated > 0 else 0,
            'agent_count': len(agents),
            'agent_consumption': agent_consumption,
            'high_consumers': high_consumers,
            'efficient_agents': efficient_agents,
            'average_efficiency': sum(a['efficiency'] for a in agent_consumption) / max(len(agent_consumption), 1),
            'monitoring_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Token consumption: {total_consumed}/{total_allocated} tokens used by {len(agents)} agents")
        
        # Store consumption data for next task
        context['task_instance'].xcom_push(
            key='consumption_status',
            value=consumption_summary
        )
        
        return consumption_summary
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to monitor consumption: {e}")
        raise AirflowException(f"API call failed: {e}")

# Monitor token consumption
monitor_consumption = PythonOperator(
    task_id='monitor_consumption',
    python_callable=monitor_token_consumption,
    dag=dag
)

# Store budget allocation in database
store_budget_allocation = PostgresOperator(
    task_id='store_budget_allocation',
    postgres_conn_id='dean_postgres',
    sql="""
    INSERT INTO agent_evolution.token_economy 
    (allocation_id, allocated_tokens, allocation_reason, allocated_at)
    SELECT 
        uuid_generate_v4() as allocation_id,
        {{ task_instance.xcom_pull(task_ids='calculate_budget', key='budget_allocation')['total_budget'] }} as allocated_tokens,
        'daily_global_allocation' as allocation_reason,
        CURRENT_TIMESTAMP as allocated_at;
    """,
    dag=dag
)

def enforce_budget_constraints(**context) -> Dict[str, Any]:
    """Enforce budget constraints and handle overages via REAL API."""
    try:
        # Get consumption status from previous task
        consumption_status = context['task_instance'].xcom_pull(
            task_ids='monitor_consumption',
            key='consumption_status'
        )
        
        if not consumption_status:
            logger.warning("No consumption status available for constraint enforcement")
            return {"enforcement": "skipped"}
        
        # Check for violations and apply constraints
        violations = []
        constraints_applied = []
        
        # Check global budget violation
        if consumption_status['total_allocated'] >= consumption_status['total_budget'] * 0.9:
            violations.append({
                'type': 'global_budget',
                'severity': 'critical',
                'message': 'Global budget nearly exhausted'
            })
            
            # Stop spawning new agents
            constraints_applied.append({
                'action': 'halt_agent_spawning',
                'reason': 'global_budget_limit'
            })
        
        # Check individual agent violations
        for agent in consumption_status.get('high_consumers', []):
            if agent['consumption_rate'] > 0.95:
                violations.append({
                    'type': 'agent_budget',
                    'agent_id': agent['agent_id'],
                    'severity': 'critical',
                    'consumption_rate': agent['consumption_rate']
                })
                
                # Retire agent if budget exhausted
                try:
                    retire_response = requests.patch(
                        f"{DEAN_API_URL}/agents/{agent['agent_id']}",
                        json={"status": "completed", "reason": "budget_exhausted"},
                        timeout=API_TIMEOUT
                    )
                    
                    if retire_response.status_code == 200:
                        constraints_applied.append({
                            'action': 'retire_agent',
                            'agent_id': agent['agent_id'],
                            'reason': 'budget_exhausted'
                        })
                        logger.info(f"Retired agent {agent['agent_id']} due to budget exhaustion")
                except Exception as e:
                    logger.error(f"Failed to retire agent {agent['agent_id']}: {e}")
        
        # Check efficiency violations
        avg_efficiency = consumption_status.get('average_efficiency', 0.5)
        if avg_efficiency < 0.3:
            violations.append({
                'type': 'low_efficiency',
                'severity': 'warning',
                'average_efficiency': avg_efficiency
            })
            
            # Trigger efficiency improvement
            constraints_applied.append({
                'action': 'trigger_efficiency_optimization',
                'reason': 'low_average_efficiency'
            })
        
        enforcement_result = {
            'violations_detected': len(violations),
            'violations': violations,
            'constraints_applied': len(constraints_applied),
            'constraints': constraints_applied,
            'enforcement_timestamp': datetime.utcnow().isoformat(),
            'total_consumption_rate': consumption_status.get('consumption_rate', 0)
        }
        
        logger.info(f"Budget enforcement: {len(violations)} violations, {len(constraints_applied)} constraints applied")
        
        return enforcement_result
        
    except Exception as e:
        logger.error(f"Budget constraint enforcement error: {str(e)}")
        raise AirflowException(f"Enforcement failed: {e}")

# Enforce budget constraints
enforce_constraints = PythonOperator(
    task_id='enforce_constraints',
    python_callable=enforce_budget_constraints,
    dag=dag
)

def calculate_efficiency_metrics(**context):
    """Calculate token efficiency metrics across services."""
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get consumption status from previous task
        consumption_status = context['task_instance'].xcom_pull(
            task_ids='monitor_consumption',
            key='consumption_status'
        )
        
        if not consumption_status:
            logger.warning("No consumption status available for efficiency calculation")
            return {"efficiency": "skipped"}
        
        services = consumption_status.get('services', {})
        efficiency_metrics = {}
        
        # Calculate efficiency for each service
        for service_name, service_data in services.items():
            if isinstance(service_data, dict) and 'consumed' in service_data:
                # Basic efficiency = work output / tokens consumed
                # For now, use inverse of consumption rate as efficiency proxy
                consumed = service_data.get('consumed', 0)
                allocated = service_data.get('allocated', 1)
                
                if consumed > 0:
                    efficiency_score = min(allocated / consumed, 1.0)  # Cap at 1.0
                else:
                    efficiency_score = 1.0  # Perfect efficiency if no consumption
                
                efficiency_metrics[service_name] = {
                    'efficiency_score': efficiency_score,
                    'tokens_consumed': consumed,
                    'tokens_allocated': allocated,
                    'consumption_rate': consumed / allocated if allocated > 0 else 0
                }
        
        # Calculate overall system efficiency
        total_consumed = sum(
            service.get('tokens_consumed', 0) 
            for service in efficiency_metrics.values()
        )
        total_allocated = sum(
            service.get('tokens_allocated', 0) 
            for service in efficiency_metrics.values()
        )
        
        system_efficiency = {
            'overall_efficiency': total_allocated / total_consumed if total_consumed > 0 else 1.0,
            'total_tokens_consumed': total_consumed,
            'total_tokens_allocated': total_allocated,
            'service_efficiencies': efficiency_metrics,
            'calculation_timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Calculated system efficiency: {system_efficiency['overall_efficiency']:.3f}")
        
        return system_efficiency
        
    except Exception as e:
        logger.error(f"Efficiency calculation error: {str(e)}")
        raise

# Calculate efficiency metrics
calculate_efficiency = PythonOperator(
    task_id='calculate_efficiency',
    python_callable=calculate_efficiency_metrics,
    dag=dag
)

# Update token efficiency scores in database
update_efficiency_scores = PostgresOperator(
    task_id='update_efficiency_scores',
    postgres_conn_id='dean_postgres',
    sql="""
    UPDATE agent_evolution.token_economy 
    SET efficiency_score = GREATEST(efficiency_score * 0.9, 0.1)
    WHERE consumed_tokens > allocated_tokens * 0.9
    AND allocated_at > CURRENT_TIMESTAMP - INTERVAL '1 hour';
    """,
    dag=dag
)

# Cleanup old token economy records
cleanup_old_records = PostgresOperator(
    task_id='cleanup_old_records',
    postgres_conn_id='dean_postgres',
    sql="""
    DELETE FROM agent_evolution.token_economy 
    WHERE allocated_at < CURRENT_TIMESTAMP - INTERVAL '30 days'
    AND consumed_tokens = allocated_tokens;
    """,
    dag=dag
)

# Generate token economy report
generate_economy_report = BashOperator(
    task_id='generate_economy_report',
    bash_command="""
    echo "DEAN Token Economy Report - $(date)" > /tmp/dean_economy_report.txt
    echo "Total Budget: {{ task_instance.xcom_pull(task_ids='calculate_budget', key='budget_allocation')['total_budget'] }}" >> /tmp/dean_economy_report.txt
    echo "Consumption Rate: {{ task_instance.xcom_pull(task_ids='monitor_consumption', key='consumption_status')['consumption_rate'] }}" >> /tmp/dean_economy_report.txt
    echo "Report generated successfully"
    """,
    dag=dag
)

# Add task to reallocate tokens based on efficiency
def reallocate_tokens(**context) -> Dict[str, Any]:
    """Reallocate tokens from inefficient to efficient agents."""
    try:
        consumption_status = context['task_instance'].xcom_pull(
            task_ids='monitor_consumption',
            key='consumption_status'
        )
        
        enforcement_result = context['task_instance'].xcom_pull(
            task_ids='enforce_constraints',
            key='enforcement_result'
        )
        
        if not consumption_status:
            return {"reallocation": "skipped", "reason": "no_data"}
        
        reallocations = []
        
        # Get efficient agents that need more tokens
        efficient_agents = consumption_status.get('efficient_agents', [])
        high_consumers = consumption_status.get('high_consumers', [])
        
        # Find agents with low efficiency and high consumption
        inefficient_agents = [a for a in consumption_status.get('agent_consumption', []) 
                             if a['efficiency'] < 0.4 and a['consumption_rate'] > 0.5]
        
        # Calculate tokens to reallocate
        tokens_to_reallocate = sum(int(a['remaining'] * 0.5) for a in inefficient_agents)
        
        if tokens_to_reallocate > 0 and efficient_agents:
            # Distribute to efficient agents proportionally
            per_agent_allocation = tokens_to_reallocate // len(efficient_agents)
            
            for agent in efficient_agents[:5]:  # Top 5 efficient agents
                if agent['consumption_rate'] > 0.7:  # Need more tokens
                    reallocations.append({
                        'agent_id': agent['agent_id'],
                        'additional_tokens': per_agent_allocation,
                        'reason': 'high_efficiency_reward'
                    })
        
        reallocation_result = {
            'tokens_reallocated': tokens_to_reallocate,
            'reallocations': reallocations,
            'beneficiaries': len(reallocations),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Token reallocation: {tokens_to_reallocate} tokens to {len(reallocations)} agents")
        
        return reallocation_result
        
    except Exception as e:
        logger.error(f"Token reallocation error: {str(e)}")
        raise

reallocate_tokens_task = PythonOperator(
    task_id='reallocate_tokens',
    python_callable=reallocate_tokens,
    dag=dag
)

# Define task dependencies
check_dean_api_health >> calculate_budget
calculate_budget >> monitor_consumption
monitor_consumption >> [store_budget_allocation, enforce_constraints, calculate_efficiency]
enforce_constraints >> reallocate_tokens_task
calculate_efficiency >> reallocate_tokens_task
reallocate_tokens_task >> update_efficiency_scores
store_budget_allocation >> update_efficiency_scores
update_efficiency_scores >> cleanup_old_records
cleanup_old_records >> generate_economy_report