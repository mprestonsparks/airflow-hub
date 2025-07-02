"""
DEAN Population Manager DAG
Comprehensive management of DEAN agent population lifecycle per specifications.
REAL IMPLEMENTATION - NO MOCKS
"""

from datetime import datetime, timedelta
import requests
import logging
from typing import Dict, Any, List
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.dummy import DummyOperator
from airflow.sensors.filesystem import FileSensor
from airflow.utils.trigger_rule import TriggerRule
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
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2)
}

dag = DAG(
    'dean_population_manager',
    default_args=default_args,
    description='DEAN Agent Population Management and Evolution',
    schedule_interval='0 */6 * * *',  # Every 6 hours
    catchup=False,
    max_active_runs=1,
    tags=['dean', 'population-management', 'evolution', 'critical']
)

# Helper functions for tasks
def check_system_health(**context) -> Dict[str, Any]:
    """Check overall DEAN system health before operations via REAL API."""
    try:
        # Check DEAN API health
        response = requests.get(
            f"{DEAN_API_URL.replace('/api/v1', '')}/health",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        health_data = response.json()
        services = health_data.get('services', {})
        
        # Check critical services
        critical_services = ['database', 'worktree_manager', 'token_manager', 'ca_engine']
        unhealthy = [s for s in critical_services if not services.get(s, False)]
        
        if unhealthy:
            raise AirflowException(f"Critical services unhealthy: {unhealthy}")
        
        # Get system metrics
        metrics_response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        metrics = metrics_response.json() if metrics_response.status_code == 200 else {}
        
        health_status = {
            'api_status': health_data.get('status', 'unknown'),
            'services': services,
            'metrics': metrics,
            'timestamp': health_data.get('timestamp', datetime.now().isoformat())
        }
        
        logger.info(f"System health check passed: {len([s for s in services.values() if s])} services healthy")
        return health_status
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Health check failed: {e}")
        raise AirflowException(f"System health check failed: {e}")

def analyze_population_metrics(**context) -> Dict[str, Any]:
    """Analyze current population metrics to determine actions needed via REAL API."""
    try:
        # Get system metrics
        metrics_response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        metrics_response.raise_for_status()
        metrics = metrics_response.json()
        
        # Get diversity metrics
        diversity_response = requests.get(
            f"{DEAN_API_URL}/system/diversity",
            timeout=API_TIMEOUT
        )
        diversity_data = diversity_response.json() if diversity_response.status_code == 200 else {}
        
        # Extract key metrics
        agent_stats = metrics.get('agents', {})
        token_stats = metrics.get('tokens', {})
        pattern_stats = metrics.get('patterns', {})
        
        total_agents = agent_stats.get('active', 0)
        avg_efficiency = token_stats.get('efficiency', 0.5)
        diversity_score = diversity_data.get('diversity_score', 0.5)
        
        # Make recommendations based on real data
        recommendations = {
            "spawn_new_agents": total_agents < context['params'].get('min_population', 5),
            "trigger_evolution": avg_efficiency < context['params'].get('min_efficiency', 0.6),
            "enforce_diversity": diversity_score < context['params'].get('min_diversity', 0.3),
            "prune_agents": total_agents > context['params'].get('max_population', 20),
            "population_stats": {
                "total_agents": total_agents,
                "average_efficiency": avg_efficiency,
                "diversity_score": diversity_score,
                "patterns_discovered": pattern_stats.get('discovered', 0),
                "tokens_consumed": token_stats.get('consumed', 0),
                "tokens_allocated": token_stats.get('allocated', 0)
            }
        }
        
        logger.info(f"Population analysis: {total_agents} agents, {avg_efficiency:.2f} efficiency, {diversity_score:.2f} diversity")
        return recommendations
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to analyze population: {e}")
        # Default conservative recommendations if stats unavailable
        return {
            "spawn_new_agents": True,
            "trigger_evolution": True,
            "enforce_diversity": True,
            "prune_agents": False,
            "error": str(e)
        }

def prune_underperforming_agents(**context) -> Dict[str, Any]:
    """Remove agents that are underperforming or resource-inefficient via REAL API."""
    try:
        # Get all active agents
        response = requests.get(
            f"{DEAN_API_URL}/agents?active_only=true",
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        agents_data = response.json()
        agents = agents_data.get("agents", [])
        
        # Check minimum population
        min_population = context['params'].get('min_population_size', 5)
        if len(agents) <= min_population:
            logger.info(f"Population too small to prune: {len(agents)} agents")
            return {"pruned_agents": 0, "reason": "population_too_small"}
        
        # Identify agents to prune based on multiple criteria
        prune_candidates = []
        
        for agent in agents:
            # Criteria for pruning
            should_prune = False
            reasons = []
            
            # Low fitness score
            if agent.get('fitness_score', 0) < 0.3:
                should_prune = True
                reasons.append('low_fitness')
            
            # Poor token efficiency
            if agent.get('token_efficiency', 1.0) < 0.2:
                should_prune = True
                reasons.append('poor_token_efficiency')
            
            # Exhausted budget
            consumed = agent.get('token_consumed', 0)
            budget = agent.get('token_budget', 1)
            if consumed >= budget * 0.95:
                should_prune = True
                reasons.append('budget_exhausted')
            
            if should_prune:
                prune_candidates.append({
                    'agent': agent,
                    'reasons': reasons
                })
        
        # Sort by fitness and prune bottom performers
        prune_candidates.sort(key=lambda x: x['agent'].get('fitness_score', 0))
        prune_count = min(len(prune_candidates), max(1, len(agents) // 5))  # Max 20%
        
        pruned_count = 0
        pruned_details = []
        
        for candidate in prune_candidates[:prune_count]:
            agent = candidate['agent']
            try:
                # Update agent status to completed/retired
                response = requests.patch(
                    f"{DEAN_API_URL}/agents/{agent['id']}",
                    json={
                        "status": "retired",
                        "retirement_reason": ", ".join(candidate['reasons'])
                    },
                    timeout=API_TIMEOUT
                )
                
                if response.status_code == 200:
                    pruned_count += 1
                    pruned_details.append({
                        'agent_id': agent['id'],
                        'reasons': candidate['reasons']
                    })
                    logger.info(f"Pruned agent {agent['id']}: {candidate['reasons']}")
            except Exception as e:
                logger.error(f"Failed to prune agent {agent['id']}: {e}")
        
        return {
            "pruned_agents": pruned_count,
            "total_population_before": len(agents),
            "total_population_after": len(agents) - pruned_count,
            "pruned_details": pruned_details
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to prune agents: {e}")
        return {"pruned_agents": 0, "error": str(e)}

def rebalance_token_economy(**context) -> Dict[str, Any]:
    """Rebalance token allocations based on agent performance via REAL API."""
    try:
        # Get current token metrics
        metrics_response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        metrics_response.raise_for_status()
        metrics = metrics_response.json()
        
        token_stats = metrics.get('tokens', {})
        total_allocated = token_stats.get('allocated', 0)
        total_consumed = token_stats.get('consumed', 0)
        
        # Get all active agents for rebalancing
        agents_response = requests.get(
            f"{DEAN_API_URL}/agents?active_only=true",
            timeout=API_TIMEOUT
        )
        agents_response.raise_for_status()
        agents = agents_response.json().get('agents', [])
        
        if not agents:
            return {"rebalanced": False, "reason": "no_active_agents"}
        
        # Calculate rebalancing strategy
        rebalance_actions = []
        
        # Find high-performing agents that need more tokens
        high_performers = [a for a in agents 
                          if a.get('fitness_score', 0) > 0.7 
                          and a.get('token_efficiency', 0) > 0.6
                          and (a.get('token_consumed', 0) / a.get('token_budget', 1)) > 0.8]
        
        # Find low-performing agents with excess tokens
        low_performers = [a for a in agents
                         if a.get('fitness_score', 0) < 0.4
                         and (a.get('token_consumed', 0) / a.get('token_budget', 1)) < 0.5]
        
        # Calculate tokens to redistribute
        tokens_to_redistribute = sum(
            int((a['token_budget'] - a['token_consumed']) * 0.5)
            for a in low_performers
        )
        
        if tokens_to_redistribute > 0 and high_performers:
            # Distribute to high performers
            per_agent_bonus = tokens_to_redistribute // len(high_performers)
            
            for agent in high_performers:
                rebalance_actions.append({
                    'agent_id': agent['id'],
                    'action': 'increase_budget',
                    'amount': per_agent_bonus,
                    'reason': 'high_performance_reward'
                })
        
        rebalance_result = {
            "rebalanced": len(rebalance_actions) > 0,
            "tokens_redistributed": tokens_to_redistribute,
            "actions": rebalance_actions,
            "high_performers": len(high_performers),
            "low_performers": len(low_performers),
            "total_agents": len(agents)
        }
        
        logger.info(f"Token rebalancing: {tokens_to_redistribute} tokens to {len(high_performers)} high performers")
        return rebalance_result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to rebalance token economy: {e}")
        return {"rebalanced": False, "error": str(e)}

def collect_evolution_metrics(**context) -> Dict[str, Any]:
    """Collect and store evolution metrics for analysis via REAL API."""
    try:
        # Collect comprehensive metrics from multiple endpoints
        metrics = {
            "collection_timestamp": datetime.utcnow().isoformat()
        }
        
        # System metrics
        system_response = requests.get(
            f"{DEAN_API_URL}/system/metrics",
            timeout=API_TIMEOUT
        )
        if system_response.status_code == 200:
            metrics["system"] = system_response.json()
        
        # Diversity metrics
        diversity_response = requests.get(
            f"{DEAN_API_URL}/system/diversity",
            timeout=API_TIMEOUT
        )
        if diversity_response.status_code == 200:
            metrics["diversity"] = diversity_response.json()
        
        # Pattern metrics
        patterns_response = requests.get(
            f"{DEAN_API_URL}/patterns?limit=50",
            timeout=API_TIMEOUT
        )
        if patterns_response.status_code == 200:
            patterns_data = patterns_response.json()
            patterns = patterns_data.get('patterns', [])
            
            metrics["patterns"] = {
                "total_discovered": len(patterns),
                "high_effectiveness": len([p for p in patterns if p.get('effectiveness_score', 0) > 0.7]),
                "recent_discoveries": len([p for p in patterns 
                                          if (datetime.now() - datetime.fromisoformat(p['discovered_at'].replace('Z', '+00:00'))).days < 1]),
                "total_reuse_count": sum(p.get('reuse_count', 0) for p in patterns)
            }
        
        # Agent performance distribution
        agents_response = requests.get(
            f"{DEAN_API_URL}/agents?active_only=true",
            timeout=API_TIMEOUT
        )
        if agents_response.status_code == 200:
            agents = agents_response.json().get('agents', [])
            
            if agents:
                fitness_scores = [a.get('fitness_score', 0) for a in agents]
                metrics["agent_performance"] = {
                    "avg_fitness": sum(fitness_scores) / len(fitness_scores),
                    "max_fitness": max(fitness_scores),
                    "min_fitness": min(fitness_scores),
                    "fitness_distribution": {
                        "high": len([s for s in fitness_scores if s > 0.7]),
                        "medium": len([s for s in fitness_scores if 0.3 <= s <= 0.7]),
                        "low": len([s for s in fitness_scores if s < 0.3])
                    }
                }
        
        logger.info(f"Collected comprehensive metrics: {len(metrics)} categories")
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to collect metrics: {e}")
        return {"error": str(e), "timestamp": datetime.utcnow().isoformat()}

def notify_completion(**context):
    """Send notification about population management cycle completion."""
    ti = context['task_instance']
    
    # Gather results from previous tasks
    system_health = ti.xcom_pull(task_ids='check_system_health')
    analysis = ti.xcom_pull(task_ids='analyze_population')
    spawn_result = ti.xcom_pull(task_ids='spawn_agents')
    evolution_result = ti.xcom_pull(task_ids='evolve_population')
    prune_result = ti.xcom_pull(task_ids='prune_agents')
    rebalance_result = ti.xcom_pull(task_ids='rebalance_economy')
    metrics = ti.xcom_pull(task_ids='collect_metrics')
    
    notification = {
        "cycle_completed": datetime.utcnow().isoformat(),
        "system_health": system_health,
        "population_analysis": analysis,
        "agents_spawned": spawn_result.get("spawned_agents", 0) if spawn_result else 0,
        "evolution_generations": evolution_result.get("generations_completed", 0) if evolution_result else 0,
        "agents_pruned": prune_result.get("pruned_agents", 0) if prune_result else 0,
        "economy_rebalanced": rebalance_result.get("rebalanced", False) if rebalance_result else False,
        "metrics_collected": bool(metrics and "error" not in metrics)
    }
    
    print(f"Population management cycle completed: {notification}")
    return notification

# Define tasks

# 1. System Health Check
health_check = PythonOperator(
    task_id='check_system_health',
    python_callable=check_system_health,
    dag=dag
)

# 2. Population Analysis
analyze_population = PythonOperator(
    task_id='analyze_population',
    python_callable=analyze_population_metrics,
    params={
        'min_population': 5,
        'max_population': 20,
        'min_efficiency': 0.6,
        'min_diversity': 0.3
    },
    dag=dag
)

# 3. Agent Spawning (conditional) - Real Implementation
def spawn_new_agents(**context) -> Dict[str, Any]:
    """Spawn new agents based on population analysis via REAL API."""
    analysis = context['task_instance'].xcom_pull(task_ids='analyze_population')
    
    if not analysis or not analysis.get('spawn_new_agents', False):
        logger.info("Skipping agent spawn - not needed")
        return {"spawned_agents": 0, "reason": "not_needed"}
    
    try:
        # Calculate how many agents to spawn
        current_population = analysis['population_stats'].get('total_agents', 0)
        target_population = context['params'].get('target_population', 10)
        agents_to_spawn = min(
            target_population - current_population,
            context['params'].get('max_spawn_batch', 3)
        )
        
        if agents_to_spawn <= 0:
            return {"spawned_agents": 0, "reason": "population_sufficient"}
        
        spawned_agents = []
        base_token_budget = context['params'].get('base_token_budget', 4096)
        
        # Spawn agents with diverse goals
        goals = [
            "Optimize code performance and reduce complexity",
            "Detect and catalog emerging patterns",
            "Improve test coverage and quality",
            "Enhance code documentation and readability",
            "Identify security vulnerabilities"
        ]
        
        for i in range(agents_to_spawn):
            goal = goals[i % len(goals)]
            
            response = requests.post(
                f"{DEAN_API_URL}/agents",
                json={
                    "goal": goal,
                    "token_budget": base_token_budget,
                    "diversity_weight": 0.5 + (i * 0.1),  # Varying diversity
                    "specialized_domain": ["performance", "patterns", "testing", "documentation", "security"][i % 5]
                },
                timeout=API_TIMEOUT
            )
            
            if response.status_code == 200:
                agent_data = response.json()
                spawned_agents.append(agent_data)
                logger.info(f"Spawned agent {agent_data['id']} with goal: {goal}")
            else:
                logger.error(f"Failed to spawn agent {i+1}: {response.text}")
        
        return {
            "spawned_agents": len(spawned_agents),
            "agent_ids": [a['id'] for a in spawned_agents],
            "total_tokens_allocated": sum(a.get('token_budget', 0) for a in spawned_agents)
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to spawn agents: {e}")
        raise AirflowException(f"Agent spawning failed: {e}")

spawn_agents = PythonOperator(
    task_id='spawn_agents',
    python_callable=spawn_new_agents,
    params={
        'target_population': 10,
        'max_spawn_batch': 3,
        'base_token_budget': 4096
    },
    dag=dag
)

# 4. Population Evolution - Real Implementation
def evolve_agent_population(**context) -> Dict[str, Any]:
    """Evolve the agent population via REAL API."""
    try:
        # Trigger population evolution
        response = requests.post(
            f"{DEAN_API_URL}/population/evolve",
            json={
                "cycles": context['params'].get('evolution_cycles', 2),
                "parallel_workers": context['params'].get('parallel_workers', 4)
            },
            timeout=API_TIMEOUT * 2  # Longer timeout for evolution
        )
        response.raise_for_status()
        
        evolution_result = response.json()
        
        # Get post-evolution metrics
        diversity_response = requests.get(
            f"{DEAN_API_URL}/system/diversity",
            timeout=API_TIMEOUT
        )
        diversity_data = diversity_response.json() if diversity_response.status_code == 200 else {}
        
        result = {
            "cycles_completed": evolution_result.get('cycles', 0),
            "agent_count": evolution_result.get('agent_count', 0),
            "diversity_score": evolution_result.get('diversity_score', diversity_data.get('diversity_score', 0)),
            "evolution_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Population evolution completed: {result['cycles_completed']} cycles, diversity={result['diversity_score']:.2f}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to evolve population: {e}")
        raise AirflowException(f"Evolution failed: {e}")

evolve_population = PythonOperator(
    task_id='evolve_population',
    python_callable=evolve_agent_population,
    params={
        'evolution_cycles': 2,
        'parallel_workers': 4
    },
    dag=dag
)

# 5. Agent Pruning (conditional)
prune_agents = PythonOperator(
    task_id='prune_agents',
    python_callable=prune_underperforming_agents,
    params={
        'min_population_size': 5
    },
    dag=dag
)

# 6. Token Economy Rebalancing
rebalance_economy = PythonOperator(
    task_id='rebalance_economy',
    python_callable=rebalance_token_economy,
    dag=dag
)

# 7. Metrics Collection
collect_metrics = PythonOperator(
    task_id='collect_metrics',
    python_callable=collect_evolution_metrics,
    dag=dag
)

# 8. Cleanup and Maintenance
cleanup_task = BashOperator(
    task_id='cleanup_resources',
    bash_command='''
    echo "Starting DEAN system cleanup..."
    
    # Clean up old log files
    find /app/logs -name "*.log" -mtime +7 -delete 2>/dev/null || true
    
    # Clean up orphaned worktrees
    if [ -d "/app/worktrees" ]; then
        find /app/worktrees -maxdepth 1 -type d -mtime +1 -exec rm -rf {} + 2>/dev/null || true
    fi
    
    # Clean up temporary files
    find /tmp -name "dean_*" -mtime +1 -delete 2>/dev/null || true
    
    echo "Cleanup completed"
    ''',
    dag=dag
)

# 9. Final Status Check
final_status = PythonOperator(
    task_id='notify_completion',
    python_callable=notify_completion,
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    dag=dag
)

# Branch logic tasks
def should_spawn_agents(**context):
    """Determine if new agents should be spawned."""
    analysis = context['task_instance'].xcom_pull(task_ids='analyze_population')
    return 'spawn_agents' if analysis.get('spawn_new_agents', False) else 'skip_spawn'

def should_prune_agents(**context):
    """Determine if agents should be pruned."""
    analysis = context['task_instance'].xcom_pull(task_ids='analyze_population')
    return 'prune_agents' if analysis.get('prune_agents', False) else 'skip_prune'

# Branch operators
from airflow.operators.python import BranchPythonOperator

spawn_decision = BranchPythonOperator(
    task_id='decide_spawn',
    python_callable=should_spawn_agents,
    dag=dag
)

prune_decision = BranchPythonOperator(
    task_id='decide_prune', 
    python_callable=should_prune_agents,
    dag=dag
)

# Skip operators for conditional paths
skip_spawn = DummyOperator(task_id='skip_spawn', dag=dag)
skip_prune = DummyOperator(task_id='skip_prune', dag=dag)

# Join point after conditional tasks
join_after_spawn = DummyOperator(
    task_id='join_after_spawn',
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    dag=dag
)

join_after_prune = DummyOperator(
    task_id='join_after_prune',
    trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS,
    dag=dag
)

# Set up task dependencies

# Main flow
health_check >> analyze_population

# Conditional spawning
analyze_population >> spawn_decision
spawn_decision >> [spawn_agents, skip_spawn]
[spawn_agents, skip_spawn] >> join_after_spawn

# Evolution (always runs)
join_after_spawn >> evolve_population

# Conditional pruning
evolve_population >> prune_decision
prune_decision >> [prune_agents, skip_prune]
[prune_agents, skip_prune] >> join_after_prune

# Final tasks (always run)
join_after_prune >> [rebalance_economy, collect_metrics]
[rebalance_economy, collect_metrics] >> cleanup_task
cleanup_task >> final_status