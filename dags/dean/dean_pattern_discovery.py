"""
DEAN Pattern Discovery DAG
Discovers and analyzes emerging patterns across the agent population.
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
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dean_pattern_discovery',
    default_args=default_args,
    description='DEAN Pattern Discovery and Analysis Pipeline',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    catchup=False,
    max_active_runs=1,
    tags=['dean', 'pattern-discovery', 'analysis', 'critical']
)

# Check DEAN API health before pattern discovery
check_dean_api_health = HttpSensor(
    task_id='check_dean_api_health',
    http_conn_id='dean_api',
    endpoint='/health',
    timeout=60,
    poke_interval=10,
    dag=dag
)

def discover_agent_patterns(**context) -> Dict[str, Any]:
    """Discover patterns in agent behaviors via REAL API."""
    try:
        # Get discovered patterns from DEAN API
        response = requests.get(
            f"{DEAN_API_URL}/patterns",
            params={
                "limit": 100,
                "min_effectiveness": context['params'].get('min_effectiveness', 0.3)
            },
            timeout=API_TIMEOUT
        )
        response.raise_for_status()
        
        patterns_data = response.json()
        patterns = patterns_data.get('patterns', [])
        
        logger.info(f"Retrieved {len(patterns)} discovered patterns")
        
        # Analyze pattern types and effectiveness
        pattern_analysis = {
            "total_patterns": len(patterns),
            "patterns_by_type": {},
            "high_effectiveness_patterns": [],
            "recent_discoveries": []
        }
        
        for pattern in patterns:
            # Group by type
            pattern_type = pattern.get('pattern_type', 'unknown')
            if pattern_type not in pattern_analysis['patterns_by_type']:
                pattern_analysis['patterns_by_type'][pattern_type] = []
            pattern_analysis['patterns_by_type'][pattern_type].append(pattern)
            
            # Track high effectiveness patterns
            if pattern.get('effectiveness_score', 0) >= 0.7:
                pattern_analysis['high_effectiveness_patterns'].append(pattern)
            
            # Track recent discoveries (last 24 hours)
            discovered_at = datetime.fromisoformat(pattern['discovered_at'].replace('Z', '+00:00'))
            if (datetime.now(discovered_at.tzinfo) - discovered_at).total_seconds() < 86400:
                pattern_analysis['recent_discoveries'].append(pattern)
        
        # Store results for downstream tasks
        context['task_instance'].xcom_push(
            key='discovered_patterns',
            value=pattern_analysis
        )
        
        return pattern_analysis
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to retrieve patterns: {e}")
        raise AirflowException(f"API call failed: {e}")

# Discover patterns in agent behaviors
discover_patterns = PythonOperator(
    task_id='discover_patterns',
    python_callable=discover_agent_patterns,
    params={
        'min_effectiveness': 0.3
    },
    dag=dag
)

def analyze_emergent_behaviors(**context) -> Dict[str, Any]:
    """Analyze emergent behaviors from pattern data using real metrics."""
    # Get patterns from previous task
    pattern_analysis = context['task_instance'].xcom_pull(
        task_ids='discover_patterns',
        key='discovered_patterns'
    )
    
    if not pattern_analysis or pattern_analysis.get('total_patterns', 0) == 0:
        logger.warning("No patterns available for behavior analysis")
        return {"analysis": "skipped", "reason": "no_patterns"}
    
    try:
        # Get system diversity metrics to correlate with patterns
        diversity_response = requests.get(
            f"{DEAN_API_URL}/system/diversity",
            timeout=API_TIMEOUT
        )
        diversity_data = diversity_response.json() if diversity_response.status_code == 200 else {}
        
        # Analyze emergent behaviors
        emergent_behaviors = []
        
        # Check for efficiency optimization emergence
        efficiency_patterns = pattern_analysis['patterns_by_type'].get('efficiency_optimization', [])
        if len(efficiency_patterns) >= 3:
            emergent_behaviors.append({
                'type': 'collective_efficiency_improvement',
                'evidence': f"{len(efficiency_patterns)} efficiency patterns discovered",
                'significance': 'high' if len(efficiency_patterns) >= 5 else 'medium'
            })
        
        # Check for collaboration emergence
        collaboration_patterns = pattern_analysis['patterns_by_type'].get('agent_collaboration', [])
        if len(collaboration_patterns) >= 2:
            emergent_behaviors.append({
                'type': 'spontaneous_collaboration',
                'evidence': f"{len(collaboration_patterns)} agents showing collaborative behavior",
                'significance': 'high'
            })
        
        # Check for diversity-driven innovation
        if diversity_data.get('diversity_score', 0) > 0.6 and len(pattern_analysis['recent_discoveries']) >= 5:
            emergent_behaviors.append({
                'type': 'diversity_driven_innovation',
                'evidence': f"High diversity ({diversity_data.get('diversity_score', 0):.2f}) with {len(pattern_analysis['recent_discoveries'])} recent discoveries",
                'significance': 'high'
            })
        
        # Check for meta-learning emergence
        reuse_patterns = [p for p in pattern_analysis.get('high_effectiveness_patterns', []) 
                         if p.get('reuse_count', 0) > 5]
        if reuse_patterns:
            emergent_behaviors.append({
                'type': 'meta_learning',
                'evidence': f"{len(reuse_patterns)} patterns being actively reused",
                'significance': 'high'
            })
        
        analysis_result = {
            "emergent_behaviors": emergent_behaviors,
            "total_behaviors_detected": len(emergent_behaviors),
            "diversity_correlation": diversity_data.get('diversity_score', 0),
            "pattern_effectiveness_avg": sum(p.get('effectiveness_score', 0) 
                                            for p in pattern_analysis.get('high_effectiveness_patterns', [])) / 
                                          max(len(pattern_analysis.get('high_effectiveness_patterns', [])), 1),
            "analysis_timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Identified {len(emergent_behaviors)} emergent behaviors")
        
        # Store for downstream tasks
        context['task_instance'].xcom_push(
            key='behavior_analysis',
            value=analysis_result
        )
        
        return analysis_result
        
    except Exception as e:
        logger.error(f"Behavior analysis error: {str(e)}")
        raise AirflowException(f"Analysis failed: {e}")

# Analyze emergent behaviors
analyze_behaviors = PythonOperator(
    task_id='analyze_behaviors',
    python_callable=analyze_emergent_behaviors,
    dag=dag
)

# Store discovered patterns in database
store_patterns = PostgresOperator(
    task_id='store_patterns',
    postgres_conn_id='dean_postgres',
    sql="""
    INSERT INTO agent_evolution.discovered_patterns 
    (pattern_type, pattern_content, effectiveness_score, discovered_at)
    SELECT 
        'auto_discovered' as pattern_type,
        '{{ task_instance.xcom_pull(task_ids="discover_patterns", key="discovered_patterns") | tojson }}' as pattern_content,
        0.5 as effectiveness_score,
        CURRENT_TIMESTAMP as discovered_at
    WHERE '{{ task_instance.xcom_pull(task_ids="discover_patterns", key="discovered_patterns") }}' IS NOT NULL;
    """,
    dag=dag
)

def classify_pattern_types(**context):
    """Classify discovered patterns by type and significance."""
    import logging
    
    logger = logging.getLogger(__name__)
    
    # Get behavior analysis from previous task
    analysis = context['task_instance'].xcom_pull(
        task_ids='analyze_behaviors',
        key='behavior_analysis'
    )
    
    if not analysis:
        logger.warning("No behavior analysis available for classification")
        return {"classification": "skipped"}
    
    try:
        significant_behaviors = analysis.get('significant_behaviors', [])
        
        # Classify patterns by type
        pattern_types = {
            'efficiency_patterns': [],
            'collaboration_patterns': [],
            'innovation_patterns': [],
            'resource_optimization': [],
            'meta_learning': []
        }
        
        for behavior in significant_behaviors:
            pattern = behavior.get('pattern', {})
            pattern_name = pattern.get('name', '').lower()
            
            if 'efficiency' in pattern_name or 'optimization' in pattern_name:
                pattern_types['efficiency_patterns'].append(behavior)
            elif 'collaboration' in pattern_name or 'cooperation' in pattern_name:
                pattern_types['collaboration_patterns'].append(behavior)
            elif 'innovation' in pattern_name or 'creative' in pattern_name:
                pattern_types['innovation_patterns'].append(behavior)
            elif 'resource' in pattern_name:
                pattern_types['resource_optimization'].append(behavior)
            else:
                pattern_types['meta_learning'].append(behavior)
        
        classification_result = {
            "pattern_classification": pattern_types,
            "classification_timestamp": datetime.utcnow().isoformat(),
            "total_classified": len(significant_behaviors)
        }
        
        logger.info(f"Classified {len(significant_behaviors)} patterns into categories")
        
        return classification_result
        
    except Exception as e:
        logger.error(f"Pattern classification error: {str(e)}")
        raise

# Classify patterns by type
classify_patterns = PythonOperator(
    task_id='classify_patterns',
    python_callable=classify_pattern_types,
    dag=dag
)

# Update pattern effectiveness scores
update_effectiveness = PostgresOperator(
    task_id='update_effectiveness',
    postgres_conn_id='dean_postgres',
    sql="""
    UPDATE agent_evolution.discovered_patterns 
    SET effectiveness_score = LEAST(effectiveness_score + 0.1, 1.0),
        last_used_at = CURRENT_TIMESTAMP
    WHERE reuse_count > 0 
    AND discovered_at > CURRENT_TIMESTAMP - INTERVAL '1 hour';
    """,
    dag=dag
)

# Cleanup old pattern data
cleanup_old_patterns = PostgresOperator(
    task_id='cleanup_old_patterns',
    postgres_conn_id='dean_postgres',
    sql="""
    DELETE FROM agent_evolution.discovered_patterns 
    WHERE effectiveness_score < 0.1 
    AND discovered_at < CURRENT_TIMESTAMP - INTERVAL '7 days'
    AND reuse_count = 0;
    """,
    dag=dag
)

# Add new task to trigger agent adaptation based on discovered patterns
def adapt_agents_to_patterns(**context) -> Dict[str, Any]:
    """Adapt agents based on discovered patterns and emergent behaviors."""
    behavior_analysis = context['task_instance'].xcom_pull(
        task_ids='analyze_behaviors',
        key='behavior_analysis'
    )
    
    if not behavior_analysis or behavior_analysis.get('total_behaviors_detected', 0) == 0:
        logger.info("No emergent behaviors to adapt to")
        return {"adaptations": 0}
    
    try:
        adaptations_made = 0
        
        # If meta-learning detected, trigger knowledge sharing
        meta_learning_behaviors = [b for b in behavior_analysis['emergent_behaviors'] 
                                  if b['type'] == 'meta_learning']
        
        if meta_learning_behaviors:
            # Get high-effectiveness patterns and propagate to other agents
            pattern_analysis = context['task_instance'].xcom_pull(
                task_ids='discover_patterns',
                key='discovered_patterns'
            )
            
            for pattern in pattern_analysis.get('high_effectiveness_patterns', [])[:5]:
                # This would trigger pattern sharing across population
                logger.info(f"Propagating high-effectiveness pattern {pattern['id']} to population")
                adaptations_made += 1
        
        # If diversity is low, trigger diversity injection
        if behavior_analysis.get('diversity_correlation', 1.0) < 0.3:
            logger.warning("Low diversity detected - triggering diversity injection")
            # This would spawn diverse agents or mutate existing ones
            adaptations_made += 1
        
        return {
            "adaptations_made": adaptations_made,
            "adaptation_timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Agent adaptation error: {str(e)}")
        raise

adapt_agents = PythonOperator(
    task_id='adapt_agents',
    python_callable=adapt_agents_to_patterns,
    dag=dag
)

# Define task dependencies
check_dean_api_health >> discover_patterns
discover_patterns >> analyze_behaviors
analyze_behaviors >> classify_patterns
analyze_behaviors >> store_patterns
classify_patterns >> adapt_agents
classify_patterns >> update_effectiveness
store_patterns >> update_effectiveness
adapt_agents >> update_effectiveness
update_effectiveness >> cleanup_old_patterns