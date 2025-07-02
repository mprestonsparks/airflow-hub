#!/usr/bin/env python3
"""
Phase 4: Airflow Integration for DEAN Evolution
A real DAG that orchestrates agent evolution cycles.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
import json
import requests
import logging


# Default arguments for the DAG
default_args = {
    'owner': 'dean_system',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'dean_evolution_orchestration',
    default_args=default_args,
    description='Orchestrates DEAN agent evolution cycles with CA and token economy',
    schedule_interval=timedelta(hours=1),  # Run hourly
    catchup=False,
    tags=['dean', 'evolution', 'cellular_automata']
)


def check_system_health(**context):
    """Check if DEAN system is healthy and ready for evolution."""
    logger = logging.getLogger(__name__)
    
    # Get DEAN API URL from Airflow Variables
    dean_api_url = Variable.get('dean_api_url', default_var='http://localhost:8091')
    
    try:
        # Check API health
        response = requests.get(f"{dean_api_url}/health", timeout=10)
        health_data = response.json()
        
        if response.status_code != 200 or health_data.get('status') != 'healthy':
            raise Exception(f"DEAN API unhealthy: {health_data}")
            
        logger.info(f"System health check passed: {health_data}")
        
        # Store health data for downstream tasks
        context['task_instance'].xcom_push(key='system_health', value=health_data)
        
        return True
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise


def get_active_agents(**context):
    """Get list of active agents ready for evolution."""
    logger = logging.getLogger(__name__)
    
    # Get database connection
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Query active agents with sufficient tokens
        cursor.execute("""
            SELECT 
                id,
                name,
                goal,
                token_budget,
                token_consumed,
                fitness_score,
                generation
            FROM agent_evolution.agents
            WHERE status = 'active'
                AND (token_budget - token_consumed) >= 500  -- Min tokens for evolution
            ORDER BY fitness_score DESC
            LIMIT 10  -- Process top 10 agents
        """)
        
        agents = []
        for row in cursor.fetchall():
            agent = {
                'id': str(row[0]),
                'name': row[1],
                'goal': row[2],
                'token_budget': row[3],
                'token_consumed': row[4],
                'fitness_score': row[5],
                'generation': row[6],
                'remaining_tokens': row[3] - row[4]
            }
            agents.append(agent)
            
        logger.info(f"Found {len(agents)} active agents ready for evolution")
        
        # Push to XCom for downstream tasks
        context['task_instance'].xcom_push(key='active_agents', value=agents)
        
        return agents
        
    finally:
        cursor.close()
        conn.close()


def check_token_economy(**context):
    """Check global token economy state and adjust strategy."""
    logger = logging.getLogger(__name__)
    
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Get global token statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as agent_count,
                SUM(token_budget) as total_allocated,
                SUM(token_consumed) as total_consumed,
                AVG(token_efficiency) as avg_efficiency
            FROM agent_evolution.agents
            WHERE status = 'active'
        """)
        
        row = cursor.fetchone()
        
        global_budget = int(Variable.get('dean_global_token_budget', default_var='1000000'))
        total_allocated = row[1] or 0
        total_consumed = row[2] or 0
        
        economy_state = {
            'agent_count': row[0] or 0,
            'total_allocated': total_allocated,
            'total_consumed': total_consumed,
            'avg_efficiency': float(row[3] or 0.5),
            'remaining_budget': global_budget - total_allocated,
            'scarcity_level': 1.0 - ((global_budget - total_allocated) / global_budget),
            'recommended_evolution_rate': 1.0  # Default
        }
        
        # Adjust evolution rate based on scarcity
        if economy_state['scarcity_level'] > 0.8:
            economy_state['recommended_evolution_rate'] = 0.3  # Slow down
            logger.warning("High token scarcity - reducing evolution rate")
        elif economy_state['scarcity_level'] > 0.6:
            economy_state['recommended_evolution_rate'] = 0.6  # Moderate
            
        logger.info(f"Token economy state: {economy_state}")
        
        context['task_instance'].xcom_push(key='economy_state', value=economy_state)
        
        return economy_state
        
    finally:
        cursor.close()
        conn.close()


def evolve_agent_batch(**context):
    """Evolve a batch of agents using DEAN API."""
    logger = logging.getLogger(__name__)
    
    # Get data from upstream tasks
    agents = context['task_instance'].xcom_pull(key='active_agents')
    economy_state = context['task_instance'].xcom_pull(key='economy_state')
    dean_api_url = Variable.get('dean_api_url', default_var='http://localhost:8091')
    
    if not agents:
        logger.info("No agents to evolve")
        return
        
    # Apply evolution rate limit
    evolution_rate = economy_state.get('recommended_evolution_rate', 1.0)
    agents_to_evolve = agents[:int(len(agents) * evolution_rate)]
    
    logger.info(f"Evolving {len(agents_to_evolve)} out of {len(agents)} agents")
    
    evolution_results = []
    
    for agent in agents_to_evolve:
        try:
            # Call DEAN API to evolve agent
            response = requests.post(
                f"{dean_api_url}/api/v1/agents/{agent['id']}/evolve",
                json={
                    'agent_id': agent['id'],
                    'generations': 1,  # One generation per Airflow run
                    'mutation_rate': 0.1
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                evolution_results.append({
                    'agent_id': agent['id'],
                    'agent_name': agent['name'],
                    'success': True,
                    'patterns_discovered': result.get('patterns_discovered', 0),
                    'tokens_consumed': result.get('tokens_consumed', 0),
                    'evolution_results': result.get('evolution_results', [])
                })
                logger.info(f"Successfully evolved agent {agent['name']}")
            else:
                evolution_results.append({
                    'agent_id': agent['id'],
                    'agent_name': agent['name'],
                    'success': False,
                    'error': response.text
                })
                logger.error(f"Failed to evolve agent {agent['name']}: {response.text}")
                
        except Exception as e:
            logger.error(f"Exception evolving agent {agent['name']}: {str(e)}")
            evolution_results.append({
                'agent_id': agent['id'],
                'agent_name': agent['name'],
                'success': False,
                'error': str(e)
            })
            
    # Store results
    context['task_instance'].xcom_push(key='evolution_results', value=evolution_results)
    
    return evolution_results


def analyze_evolution_results(**context):
    """Analyze results and record metrics."""
    logger = logging.getLogger(__name__)
    
    evolution_results = context['task_instance'].xcom_pull(key='evolution_results')
    
    if not evolution_results:
        logger.info("No evolution results to analyze")
        return
        
    # Calculate metrics
    total_evolved = len(evolution_results)
    successful_evolutions = sum(1 for r in evolution_results if r['success'])
    total_patterns = sum(r.get('patterns_discovered', 0) for r in evolution_results if r['success'])
    total_tokens = sum(r.get('tokens_consumed', 0) for r in evolution_results if r['success'])
    
    metrics = {
        'run_timestamp': context['execution_date'].isoformat(),
        'total_agents_evolved': total_evolved,
        'successful_evolutions': successful_evolutions,
        'success_rate': successful_evolutions / total_evolved if total_evolved > 0 else 0,
        'patterns_discovered': total_patterns,
        'tokens_consumed': total_tokens,
        'avg_tokens_per_evolution': total_tokens / successful_evolutions if successful_evolutions > 0 else 0
    }
    
    logger.info(f"Evolution cycle metrics: {metrics}")
    
    # Store metrics in database
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Insert metrics
        cursor.execute("""
            INSERT INTO agent_evolution.audit_log 
            (agent_id, action_type, action_description, success, target_resource, tokens_consumed)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            '00000000-0000-0000-0000-000000000000',  # System-level action
            'airflow_evolution_cycle',
            json.dumps(metrics),
            True,
            f"Evolved {successful_evolutions} agents",
            total_tokens
        ))
        
        conn.commit()
        
    finally:
        cursor.close()
        conn.close()
        
    return metrics


def check_population_diversity(**context):
    """Check population diversity and trigger interventions if needed."""
    logger = logging.getLogger(__name__)
    
    pg_hook = PostgresHook(postgres_conn_id='postgres_default')
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Calculate diversity metrics
        cursor.execute("""
            SELECT 
                COUNT(DISTINCT goal) as goal_diversity,
                STDDEV(fitness_score) as fitness_variance,
                COUNT(DISTINCT specialized_domain) as domain_diversity
            FROM agent_evolution.agents
            WHERE status = 'active'
        """)
        
        row = cursor.fetchone()
        
        diversity_metrics = {
            'goal_diversity': row[0] or 1,
            'fitness_variance': float(row[1] or 0.0),
            'domain_diversity': row[2] or 1,
            'requires_intervention': False
        }
        
        # Simple diversity score
        diversity_score = (
            (diversity_metrics['goal_diversity'] / 10.0) +  # Normalize
            (diversity_metrics['fitness_variance'] * 2.0) +  # Weight variance
            (diversity_metrics['domain_diversity'] / 5.0)
        ) / 3.0
        
        diversity_metrics['diversity_score'] = min(1.0, diversity_score)
        
        # Check if intervention needed
        if diversity_score < 0.3:
            diversity_metrics['requires_intervention'] = True
            logger.warning(f"Low population diversity ({diversity_score:.2f}) - intervention recommended")
            
        logger.info(f"Population diversity metrics: {diversity_metrics}")
        
        return diversity_metrics
        
    finally:
        cursor.close()
        conn.close()


# Define task dependencies
task_health_check = PythonOperator(
    task_id='check_system_health',
    python_callable=check_system_health,
    provide_context=True,
    dag=dag
)

task_get_agents = PythonOperator(
    task_id='get_active_agents',
    python_callable=get_active_agents,
    provide_context=True,
    dag=dag
)

task_check_economy = PythonOperator(
    task_id='check_token_economy',
    python_callable=check_token_economy,
    provide_context=True,
    dag=dag
)

task_evolve_batch = PythonOperator(
    task_id='evolve_agent_batch',
    python_callable=evolve_agent_batch,
    provide_context=True,
    dag=dag
)

task_analyze_results = PythonOperator(
    task_id='analyze_evolution_results',
    python_callable=analyze_evolution_results,
    provide_context=True,
    dag=dag
)

task_check_diversity = PythonOperator(
    task_id='check_population_diversity',
    python_callable=check_population_diversity,
    provide_context=True,
    dag=dag
)

# Set up task dependencies
task_health_check >> [task_get_agents, task_check_economy]
[task_get_agents, task_check_economy] >> task_evolve_batch
task_evolve_batch >> task_analyze_results
task_analyze_results >> task_check_diversity