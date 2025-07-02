#!/usr/bin/env python3
"""
DEAN Pattern Discovery DAG
Discovers and propagates effective patterns across agent population
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import sys
sys.path.append('/opt/airflow/plugins')
from dean_operators import (
    DEANPatternPropagationOperator,
    DEANMonitoringOperator
)
import json
import logging
import requests

# Configuration
INDEXAGENT_URL = Variable.get("indexagent_url", "http://indexagent:8081")
DEAN_ORCHESTRATOR_URL = Variable.get("dean_orchestrator_url", "http://dean-orchestrator:8082")

# Default DAG arguments
default_args = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 25),
    'email_on_failure': True,
    'email': ['dean-alerts@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=3),
}

# Create DAG
dag = DAG(
    'dean_pattern_discovery',
    default_args=default_args,
    description='Discovers and propagates patterns in DEAN system',
    schedule_interval='*/15 * * * *',  # Every 15 minutes
    catchup=False,
    tags=['dean', 'patterns', 'discovery'],
)

def discover_patterns(**context):
    """Discover new patterns from agent behaviors."""
    import requests
    import numpy as np
    
    # Get all discovered patterns
    response = requests.get(f"{INDEXAGENT_URL}/api/v1/patterns/discovered")
    patterns_data = response.json()
    
    all_patterns = patterns_data.get('patterns', [])
    total_patterns = patterns_data.get('total', 0)
    
    logging.info(f"Total patterns discovered: {total_patterns}")
    
    # Filter high-value patterns
    high_value_patterns = []
    new_patterns = []
    
    for pattern in all_patterns:
        # Check if pattern is effective
        effectiveness = pattern.get('effectiveness', 0)
        occurrences = pattern.get('occurrences', 0)
        confidence = pattern.get('confidence', 0)
        
        # Calculate pattern value score
        value_score = (
            effectiveness * 0.5 +
            min(occurrences / 10, 1.0) * 0.3 +
            confidence * 0.2
        )
        
        pattern['value_score'] = value_score
        
        # High-value patterns
        if value_score > 0.7:
            high_value_patterns.append(pattern)
        
        # New patterns (discovered in last hour)
        if pattern.get('first_seen'):
            first_seen = datetime.fromisoformat(pattern['first_seen'].replace('Z', '+00:00'))
            if (datetime.utcnow() - first_seen).total_seconds() < 3600:
                new_patterns.append(pattern)
    
    # Sort by value score
    high_value_patterns.sort(key=lambda x: x['value_score'], reverse=True)
    
    result = {
        'total_patterns': total_patterns,
        'high_value_patterns': high_value_patterns[:10],  # Top 10
        'new_patterns': new_patterns[:5],  # Latest 5
        'patterns_to_propagate': []
    }
    
    # Determine which patterns to propagate
    for pattern in high_value_patterns[:3]:  # Top 3 patterns
        if pattern.get('occurrences', 0) < 50:  # Not yet widespread
            result['patterns_to_propagate'].append(pattern)
    
    # Push to XCom
    context['task_instance'].xcom_push(key='discovered_patterns', value=result)
    
    logging.info(f"High-value patterns: {len(high_value_patterns)}")
    logging.info(f"New patterns: {len(new_patterns)}")
    logging.info(f"Patterns to propagate: {len(result['patterns_to_propagate'])}")
    
    return result

def analyze_pattern_effectiveness(**context):
    """Analyze effectiveness of previously propagated patterns."""
    import requests
    
    discovered_patterns = context['task_instance'].xcom_pull(key='discovered_patterns')
    
    if not discovered_patterns:
        return {'analysis': 'no_patterns'}
    
    # Get agents using high-value patterns
    pattern_usage = {}
    performance_correlation = {}
    
    high_value_patterns = discovered_patterns.get('high_value_patterns', [])
    
    for pattern in high_value_patterns[:5]:
        pattern_id = pattern.get('pattern_id') or pattern.get('id')
        agent_ids = pattern.get('agent_ids', [])
        
        if agent_ids:
            # Get performance of agents using this pattern
            performances = []
            
            for agent_id in agent_ids[:10]:  # Sample up to 10 agents
                try:
                    response = requests.get(f"{INDEXAGENT_URL}/api/v1/agents/{agent_id}")
                    if response.status_code == 200:
                        agent_data = response.json()
                        performances.append({
                            'fitness': agent_data.get('fitness_score', 0),
                            'efficiency': agent_data.get('token_budget', {}).get('efficiency_score', 0)
                        })
                except:
                    continue
            
            if performances:
                avg_fitness = np.mean([p['fitness'] for p in performances])
                avg_efficiency = np.mean([p['efficiency'] for p in performances])
                
                pattern_usage[pattern_id] = {
                    'agent_count': len(agent_ids),
                    'avg_fitness': avg_fitness,
                    'avg_efficiency': avg_efficiency,
                    'pattern_type': pattern.get('pattern_type'),
                    'effectiveness': pattern.get('effectiveness', 0)
                }
    
    # Analyze trends
    analysis = {
        'pattern_usage': pattern_usage,
        'most_adopted': max(pattern_usage.items(), key=lambda x: x[1]['agent_count'])[0] if pattern_usage else None,
        'most_effective': max(pattern_usage.items(), key=lambda x: x[1]['avg_fitness'])[0] if pattern_usage else None,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    # Push to XCom
    context['task_instance'].xcom_push(key='pattern_analysis', value=analysis)
    
    logging.info(f"Pattern effectiveness analysis: {json.dumps(analysis, indent=2)}")
    
    return analysis

def should_propagate_patterns(**context):
    """Decide whether to propagate patterns based on analysis."""
    discovered_patterns = context['task_instance'].xcom_pull(key='discovered_patterns')
    pattern_analysis = context['task_instance'].xcom_pull(key='pattern_analysis')
    
    # Check if we have patterns to propagate
    patterns_to_propagate = discovered_patterns.get('patterns_to_propagate', [])
    
    if not patterns_to_propagate:
        logging.info("No patterns to propagate")
        return 'skip_propagation'
    
    # Check system capacity
    response = requests.get(f"{DEAN_ORCHESTRATOR_URL}/api/v1/population/status")
    if response.status_code == 200:
        population_status = response.json()
        
        # Don't propagate if diversity is too low
        if population_status.get('population_diversity', 1.0) < 0.25:
            logging.warning("Population diversity too low for pattern propagation")
            return 'skip_propagation'
        
        # Don't propagate if token budget is low
        token_usage = population_status.get('token_usage', {})
        if token_usage.get('available', 0) < 10000:
            logging.warning("Insufficient token budget for pattern propagation")
            return 'skip_propagation'
    
    logging.info(f"Proceeding with pattern propagation: {len(patterns_to_propagate)} patterns")
    return 'propagate_patterns'

def extract_behavioral_patterns(**context):
    """Extract behavioral patterns from agent action sequences."""
    import requests
    
    # This would implement sliding window analysis
    # For now, we'll use a simplified version
    
    # Get recent agent actions
    response = requests.get(f"{INDEXAGENT_URL}/api/v1/agents")
    agents = response.json().get('agents', [])
    
    behavioral_patterns = []
    
    # Analyze top performers
    top_agents = sorted(
        [a for a in agents if a.get('status') == 'active'],
        key=lambda x: x.get('fitness_score', 0),
        reverse=True
    )[:10]
    
    for agent in top_agents:
        # In a real implementation, this would analyze action sequences
        # For now, we extract patterns from agent strategies
        strategies = agent.get('genome', {}).get('strategies', [])
        
        if len(strategies) > 3:
            # Look for strategy combinations
            for i in range(len(strategies) - 2):
                pattern = {
                    'type': 'behavioral_sequence',
                    'sequence': strategies[i:i+3],
                    'agent_fitness': agent.get('fitness_score', 0),
                    'agent_id': agent.get('id')
                }
                behavioral_patterns.append(pattern)
    
    # Deduplicate and score patterns
    unique_patterns = {}
    for pattern in behavioral_patterns:
        key = tuple(pattern['sequence'])
        if key not in unique_patterns:
            unique_patterns[key] = {
                'sequence': pattern['sequence'],
                'occurrences': 1,
                'avg_fitness': pattern['agent_fitness']
            }
        else:
            unique_patterns[key]['occurrences'] += 1
            unique_patterns[key]['avg_fitness'] = (
                unique_patterns[key]['avg_fitness'] + pattern['agent_fitness']
            ) / 2
    
    # Convert back to list and sort by value
    behavioral_patterns = []
    for sequence, data in unique_patterns.items():
        if data['occurrences'] >= 2:  # Pattern appears in multiple agents
            behavioral_patterns.append({
                'pattern_type': 'behavioral',
                'sequence': list(sequence),
                'occurrences': data['occurrences'],
                'effectiveness': data['avg_fitness'],
                'confidence': min(data['occurrences'] / 10, 1.0)
            })
    
    # Sort by effectiveness
    behavioral_patterns.sort(key=lambda x: x['effectiveness'], reverse=True)
    
    # Push to XCom
    context['task_instance'].xcom_push(
        key='behavioral_patterns',
        value=behavioral_patterns[:5]  # Top 5
    )
    
    logging.info(f"Extracted {len(behavioral_patterns)} behavioral patterns")
    
    return behavioral_patterns

def generate_pattern_report(**context):
    """Generate comprehensive pattern discovery report."""
    discovered_patterns = context['task_instance'].xcom_pull(key='discovered_patterns')
    pattern_analysis = context['task_instance'].xcom_pull(key='pattern_analysis')
    behavioral_patterns = context['task_instance'].xcom_pull(key='behavioral_patterns')
    
    report = {
        'report_timestamp': datetime.utcnow().isoformat(),
        'summary': {
            'total_patterns': discovered_patterns.get('total_patterns', 0),
            'high_value_patterns': len(discovered_patterns.get('high_value_patterns', [])),
            'new_patterns': len(discovered_patterns.get('new_patterns', [])),
            'behavioral_patterns': len(behavioral_patterns) if behavioral_patterns else 0
        },
        'top_patterns': discovered_patterns.get('high_value_patterns', [])[:3],
        'pattern_effectiveness': pattern_analysis.get('pattern_usage', {}) if pattern_analysis else {},
        'behavioral_insights': behavioral_patterns[:3] if behavioral_patterns else [],
        'recommendations': []
    }
    
    # Generate recommendations
    if discovered_patterns.get('patterns_to_propagate'):
        report['recommendations'].append(
            f"Propagate {len(discovered_patterns['patterns_to_propagate'])} high-value patterns"
        )
    
    if pattern_analysis and pattern_analysis.get('most_effective'):
        report['recommendations'].append(
            f"Focus on pattern type: {pattern_analysis['most_effective']}"
        )
    
    if behavioral_patterns and len(behavioral_patterns) > 0:
        report['recommendations'].append(
            "Integrate behavioral pattern sequences into evolution strategy"
        )
    
    # Log report
    logging.info(f"Pattern Discovery Report:\n{json.dumps(report, indent=2)}")
    
    # In production, this would be sent to a dashboard or notification system
    
    return report

# Define tasks
with dag:
    # Pattern discovery
    discover = PythonOperator(
        task_id='discover_patterns',
        python_callable=discover_patterns,
        provide_context=True,
    )
    
    # Pattern effectiveness analysis
    analyze = PythonOperator(
        task_id='analyze_pattern_effectiveness',
        python_callable=analyze_pattern_effectiveness,
        provide_context=True,
    )
    
    # Behavioral pattern extraction
    extract_behavioral = PythonOperator(
        task_id='extract_behavioral_patterns',
        python_callable=extract_behavioral_patterns,
        provide_context=True,
    )
    
    # Decision branch
    should_propagate = BranchPythonOperator(
        task_id='should_propagate_patterns',
        python_callable=should_propagate_patterns,
        provide_context=True,
    )
    
    # Pattern propagation
    propagate = DEANPatternPropagationOperator(
        task_id='propagate_patterns',
        propagation_strategy='fitness_weighted',
        max_recipients=15,
    )
    
    # Skip propagation
    skip_propagation = DummyOperator(
        task_id='skip_propagation',
    )
    
    # Monitoring
    monitor = DEANMonitoringOperator(
        task_id='collect_metrics',
        metrics_to_collect=['pattern_discovery', 'population_status'],
        trigger_rule='none_failed_or_skipped',
    )
    
    # Report generation
    report = PythonOperator(
        task_id='generate_pattern_report',
        python_callable=generate_pattern_report,
        provide_context=True,
        trigger_rule='none_failed_or_skipped',
    )
    
    # Set dependencies
    discover >> [analyze, extract_behavioral] >> should_propagate
    should_propagate >> [propagate, skip_propagation]
    [propagate, skip_propagation] >> monitor >> report