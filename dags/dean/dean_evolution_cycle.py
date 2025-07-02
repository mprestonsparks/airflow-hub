#!/usr/bin/env python3
"""
DEAN Evolution Cycle DAG
Orchestrates the complete evolution cycle for DEAN agents
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import logging

# Import DEAN components
import sys
# Use Airflow Variable for configurable path
agent_evolution_path = Variable.get("DEAN_AGENT_EVOLUTION_PATH", "/opt/agent-evolution")
if agent_evolution_path not in sys.path:
    sys.path.append(agent_evolution_path)

logger = logging.getLogger(__name__)

# Default DAG arguments
default_args = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
dag = DAG(
    'dean_evolution_cycle',
    default_args=default_args,
    description='Orchestrates DEAN agent evolution cycles',
    schedule_interval=timedelta(hours=1),  # Run every hour
    catchup=False,
    max_active_runs=1,
    tags=['dean', 'evolution', 'agents'],
)


def check_global_budget(**context) -> str:
    """Check if global budget allows new evolution cycle"""
    from dean.utils.economic_client import EconomicGovernorClient
    
    # Initialize client
    client = EconomicGovernorClient()
    
    try:
        # Get system metrics via API
        response = client.get_system_metrics()
        metrics = response['global_budget']
        
        # Check if we have budget
        available = metrics['available']
        usage_rate = metrics['usage_rate']
        
        logger.info(f"Budget check: available={available}, usage_rate={usage_rate:.2%}")
        
        # Store metrics for downstream tasks
        context['task_instance'].xcom_push(key='budget_metrics', value=response)
        
        if available < 10000:  # Minimum budget threshold
            logger.warning("Insufficient budget for evolution cycle")
            return 'insufficient_budget'
        
        return 'spawn_agents'
    except Exception as e:
        logger.error(f"Failed to check global budget: {e}")
        # Fail safe - continue with cycle
        return 'spawn_agents'
    finally:
        client.close()


def spawn_agent_generation(**context) -> List[str]:
    """Spawn a new generation of agents"""
    from IndexAgent.indexagent.agents.evolution.cellular_automata import CellularAutomataEngine
    from dean.utils.worktree_client import WorktreeClient
    from dean.utils.optimization_client import DEANOptimizer
    
    generation = context['dag_run'].conf.get('generation', 1)
    agent_count = int(Variable.get("dean_agent_count", "10"))
    base_repo = Variable.get("dean_base_repo", "/repos/target")
    
    # Initialize components
    worktree_client = WorktreeClient()
    optimizer = DEANOptimizer()
    ca_engine = CellularAutomataEngine(None, optimizer, base_repo)  # Worktree managed via API
    
    # Create initial agents or evolve from previous generation
    agent_ids = []
    
    if generation == 1:
        # Initial population
        strategies = [
            ["baseline_optimization"],
            ["test_improvement", "coverage"],
            ["refactor_complexity"],
            ["implement_todos"],
            ["parallel_execution"],
            ["caching_optimization"],
            ["error_handling"],
            ["performance_monitoring"],
            ["adaptive_learning"],
            ["hybrid_approach"]
        ]
        
        for i in range(min(agent_count, len(strategies))):
            agent_id = f"agent_gen{generation}_{i:03d}"
            ca_engine.create_agent(agent_id, strategies=strategies[i])
            agent_ids.append(agent_id)
    else:
        # Evolve from previous generation
        for i in range(agent_count):
            agent_id = f"agent_gen{generation}_{i:03d}"
            
            # Evaluate CA rules for evolution
            if i < len(ca_engine.agents):
                parent_id = list(ca_engine.agents.keys())[i % len(ca_engine.agents)]
                decisions = ca_engine.evaluate_rules(parent_id)
                
                for decision in decisions:
                    new_agent_id = ca_engine.execute_decision(decision)
                    if new_agent_id:
                        agent_ids.append(new_agent_id)
                        break
                else:
                    # No evolution decision, create with mutation
                    ca_engine.create_agent(agent_id, parent_id=parent_id)
                    agent_ids.append(agent_id)
            else:
                # Create new random agent
                ca_engine.create_agent(agent_id)
                agent_ids.append(agent_id)
    
    # Advance generation
    ca_engine.advance_generation()
    
    logger.info(f"Spawned {len(agent_ids)} agents for generation {generation}")
    return agent_ids


def execute_ca_rules(agent_id: str, **context) -> Dict[str, Any]:
    """Execute cellular automata rules for an agent"""
    from IndexAgent.indexagent.agents.evolution.cellular_automata import CellularAutomataEngine
    from IndexAgent.indexagent.actions import ImplementTodosAction, ImproveTestCoverageAction, RefactorComplexityAction
    from dean.utils.worktree_client import WorktreeClient
    from dean.utils.claude_api_client import create_claude_client
    from dean.utils.optimization_client import DEANOptimizer
    from dean.utils.economic_client import EconomicGovernorClient
    import random
    
    generation = context['dag_run'].conf.get('generation', 1)
    base_repo = Variable.get("dean_base_repo", "/repos/target")
    use_mock = Variable.get("use_mock_claude", "false").lower() == "true"
    
    # Initialize components
    worktree_client = WorktreeClient()
    optimizer = DEANOptimizer()
    ca_engine = CellularAutomataEngine(None, optimizer, base_repo)  # Worktree managed via API
    economic_client = EconomicGovernorClient()
    
    # Get agent worktree
    worktree_path = worktree_client.create_worktree(agent_id, base_repo)
    
    # Create Claude client (real or mock based on configuration)
    cli = create_claude_client(
        api_key=Variable.get("anthropic_api_key", ""),
        worktree_path=worktree_path,
        use_mock=use_mock
    )
    
    # Select action based on agent strategies
    agent = ca_engine.agents.get(agent_id)
    if not agent:
        logger.error(f"Agent {agent_id} not found")
        return {'success': False, 'error': 'Agent not found'}
    
    # Map strategies to actions
    action_map = {
        'implement_todos': ImplementTodosAction,
        'test_improvement': ImproveTestCoverageAction,
        'refactor_complexity': RefactorComplexityAction,
        'baseline_optimization': ImplementTodosAction,  # Default
    }
    
    # Select action based on strategies
    selected_action = None
    for strategy in agent.active_strategies:
        for key, action_class in action_map.items():
            if key in strategy.lower():
                selected_action = action_class()
                break
        if selected_action:
            break
    
    if not selected_action:
        # Random selection
        selected_action = random.choice(list(action_map.values()))()
    
    logger.info(f"Agent {agent_id} executing {selected_action.get_action_type()}")
    
    # Execute action
    try:
        result = selected_action.execute(worktree_path, cli, optimizer)
        
        # Record token usage via API
        try:
            economic_client.use_tokens(
                agent_id,
                result.metrics.token_cost,
                selected_action.get_action_type(),
                result.metrics.task_specific_score,
                result.metrics.quality_score
            )
        except Exception as e:
            logger.warning(f"Failed to record token usage via API: {e}")
        
        # Update agent fitness
        ca_engine.update_agent_fitness(
            agent_id,
            result.metrics.task_specific_score,
            result.metrics.token_cost,
            result.metrics.quality_score
        )
        
        # Evaluate CA rules for this agent
        decisions = ca_engine.evaluate_rules(agent_id)
        
        return {
            'agent_id': agent_id,
            'action': selected_action.get_action_type(),
            'success': result.success,
            'metrics': {
                'task_score': result.metrics.task_specific_score,
                'quality_score': result.metrics.quality_score,
                'token_cost': result.metrics.token_cost
            },
            'ca_decisions': [d.action for d in decisions]
        }
        
    except Exception as e:
        logger.error(f"Error executing action for agent {agent_id}: {e}")
        return {
            'agent_id': agent_id,
            'success': False,
            'error': str(e)
        }
    finally:
        # Cleanup
        economic_client.close()
        worktree_client.cleanup_worktree(agent_id)
        worktree_client.close()


def measure_diversity(**context) -> Dict[str, Any]:
    """Measure population diversity"""
    from dean.utils.diversity_client import DiversityManager
    
    # Get agent results from upstream
    ti = context['task_instance']
    agent_results = []
    
    # Collect results from all agent tasks
    for task_id in context['task'].upstream_task_ids:
        if task_id.startswith('agent_'):
            result = ti.xcom_pull(task_ids=task_id)
            if result:
                agent_results.append(result)
    
    # Initialize diversity manager
    diversity_manager = DiversityManager()
    
    # Register agents with their strategies
    for result in agent_results:
        if result.get('success'):
            # Mock registration - in production, get actual strategies
            diversity_manager.register_agent(
                result['agent_id'],
                strategies=['strategy1', 'strategy2'],  # Would get from CA engine
                lineage=[],
                generation=context['dag_run'].conf.get('generation', 1)
            )
    
    # Calculate diversity metrics
    metrics = diversity_manager.calculate_diversity_metrics()
    
    # Check if intervention needed
    intervention = diversity_manager.check_intervention_needed()
    
    if intervention:
        logger.warning(f"Diversity intervention needed: {intervention}")
        
        # Apply interventions
        if intervention == "low_variance":
            # Force mutations on some agents
            for result in agent_results[:3]:
                diversity_manager.force_mutation(result['agent_id'])
        elif intervention == "high_convergence":
            # Import foreign patterns
            for result in agent_results[:2]:
                diversity_manager.import_foreign_pattern(result['agent_id'])
    
    return {
        'diversity_metrics': {
            'population_variance': metrics.population_variance,
            'convergence_index': metrics.convergence_index,
            'entropy': metrics.entropy,
            'unique_strategies': metrics.unique_strategies
        },
        'intervention_applied': intervention,
        'status': diversity_manager.get_diversity_report()['diversity_status']
    }


def detect_patterns(**context) -> Dict[str, Any]:
    """Detect patterns in agent improvements"""
    from IndexAgent.indexagent.patterns.detector import PatternDetector
    from IndexAgent.indexagent.patterns.cataloger import PatternCataloger, CatalogedPattern
    import os
    
    db_url = Variable.get("dean_db_url", os.environ.get('DATABASE_URL'))
    
    # Initialize components
    detector = PatternDetector()
    cataloger = PatternCataloger(db_url)
    
    # Get agent results
    ti = context['task_instance']
    agent_results = []
    
    for task_id in context['task'].upstream_task_ids:
        if task_id.startswith('agent_'):
            result = ti.xcom_pull(task_ids=task_id)
            if result and result.get('success'):
                agent_results.append(result)
    
    # Analyze modifications for patterns
    detected_patterns = []
    
    for result in agent_results:
        # Mock git diff - in production, get actual diff
        git_diff = "- old code\n+ new optimized code"
        prompt = "Optimize the code"
        
        patterns = detector.analyze_modification(
            result['agent_id'],
            result['action'],
            git_diff,
            prompt,
            result['metrics']['task_score'],
            result['metrics']['token_cost']
        )
        
        detected_patterns.extend(patterns)
    
    # Get top patterns
    top_patterns = detector.get_top_patterns(limit=5)
    
    # Catalog significant patterns
    cataloged_count = 0
    for pattern_data in top_patterns:
        if pattern_data['type'] == 'code':
            pattern = pattern_data['pattern']
            cataloged_pattern = CatalogedPattern(
                pattern_id=pattern['pattern_id'],
                pattern_type=pattern['pattern_type'],
                action_type=pattern['action_type'],
                description=pattern['description'],
                pattern_data={'code': pattern['code_after']},
                success_metrics={'performance_delta': pattern['performance_delta']},
                discovery_agent=pattern['agent_id'],
                discovery_generation=context['dag_run'].conf.get('generation', 1),
                avg_success_delta=pattern['performance_delta']
            )
            
            cataloger.catalog_pattern(cataloged_pattern)
            cataloged_count += 1
    
    return {
        'patterns_detected': len(detected_patterns),
        'patterns_cataloged': cataloged_count,
        'top_patterns': [p['pattern']['pattern_id'] for p in top_patterns[:3]]
    }


def meta_learning_injection(**context) -> Dict[str, Any]:
    """Perform meta-learning and inject patterns"""
    from IndexAgent.indexagent.patterns.detector import PatternDetector
    from IndexAgent.indexagent.patterns.cataloger import PatternCataloger
    from IndexAgent.indexagent.patterns.meta_learner import MetaLearner
    from dean.utils.optimization_client import DEANOptimizer
    import os
    
    generation = context['dag_run'].conf.get('generation', 1)
    
    # Only run every 5 generations
    if generation % 5 != 0:
        return {'skipped': True, 'reason': 'Not a meta-learning generation'}
    
    db_url = Variable.get("dean_db_url", os.environ.get('DATABASE_URL'))
    
    # Initialize components
    detector = PatternDetector()
    cataloger = PatternCataloger(db_url)
    optimizer = DEANOptimizer()
    meta_learner = MetaLearner(detector, cataloger, optimizer)
    
    # Extract meta-patterns
    meta_patterns = meta_learner.extract_meta_patterns(generation)
    
    if not meta_patterns:
        return {'extracted': 0, 'injected': 0}
    
    # Inject into DSPy
    injected = meta_learner.inject_patterns_to_dspy(meta_patterns)
    
    # Get agent IDs from previous tasks
    ti = context['task_instance']
    agent_ids = ti.xcom_pull(task_ids='spawn_agents')
    
    # Propagate to population
    propagation_map = meta_learner.propagate_to_population(meta_patterns, agent_ids)
    
    return {
        'meta_patterns_extracted': len(meta_patterns),
        'examples_injected': injected,
        'agents_updated': len(propagation_map),
        'report': meta_learner.get_meta_learning_report()
    }


# Task definitions
with dag:
    # Check global budget
    budget_check = BranchPythonOperator(
        task_id='check_global_budget',
        python_callable=check_global_budget,
        provide_context=True,
    )
    
    # Insufficient budget path
    insufficient_budget = DummyOperator(
        task_id='insufficient_budget',
        trigger_rule='none_failed_min_one_success'
    )
    
    # Spawn agents
    spawn_agents = PythonOperator(
        task_id='spawn_agents',
        python_callable=spawn_agent_generation,
        provide_context=True,
    )
    
    # Agent execution group
    with TaskGroup(group_id='agent_execution') as agent_group:
        # Dynamic task generation would happen here
        # For demo, create fixed number of agent tasks
        agent_tasks = []
        for i in range(10):
            agent_task = PythonOperator(
                task_id=f'agent_{i:03d}',
                python_callable=execute_ca_rules,
                op_kwargs={'agent_id': f'agent_{{{{ dag_run.conf.generation }}}}_{{i:03d}}'},
                provide_context=True,
            )
            agent_tasks.append(agent_task)
    
    # Measure diversity
    diversity_check = PythonOperator(
        task_id='measure_diversity',
        python_callable=measure_diversity,
        provide_context=True,
        trigger_rule='none_failed_min_one_success'
    )
    
    # Detect patterns
    pattern_detection = PythonOperator(
        task_id='detect_patterns',
        python_callable=detect_patterns,
        provide_context=True,
    )
    
    # Meta-learning injection
    meta_learning = PythonOperator(
        task_id='meta_learning_injection',
        python_callable=meta_learning_injection,
        provide_context=True,
    )
    
    # Task dependencies
    budget_check >> [insufficient_budget, spawn_agents]
    spawn_agents >> agent_group >> diversity_check >> pattern_detection >> meta_learning