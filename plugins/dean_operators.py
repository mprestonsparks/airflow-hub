#!/usr/bin/env python3
"""
Custom Airflow Operators for DEAN System
Provides specialized operators for agent management and evolution
"""

from typing import Dict, List, Optional, Any
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
import requests
import json
import logging
from datetime import datetime

class DEANAgentSpawnOperator(BaseOperator):
    """
    Spawns new DEAN agents with specified configurations.
    """
    
    template_fields = ['population_size', 'goals', 'token_budget']
    ui_color = '#4CAF50'
    
    @apply_defaults
    def __init__(
        self,
        population_size: int,
        goals: List[str],
        token_budget: int = 5000,
        genome_template: str = "default",
        diversity_target: float = 0.35,
        dean_orchestrator_url: str = "http://dean-orchestrator:8082",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.population_size = population_size
        self.goals = goals
        self.token_budget = token_budget
        self.genome_template = genome_template
        self.diversity_target = diversity_target
        self.dean_orchestrator_url = dean_orchestrator_url
    
    def execute(self, context):
        """Execute agent spawn operation."""
        self.log.info(f"Spawning {self.population_size} agents")
        
        spawn_request = {
            "population_size": self.population_size,
            "genome_template": self.genome_template,
            "token_budget": self.token_budget,
            "goals": self.goals,
            "diversity_target": self.diversity_target
        }
        
        try:
            response = requests.post(
                f"{self.dean_orchestrator_url}/api/v1/agents/spawn",
                json=spawn_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log.info(f"Successfully spawned {len(result.get('agent_ids', []))} agents")
                return result
            else:
                raise AirflowException(f"Agent spawn failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise AirflowException(f"Network error during agent spawn: {str(e)}")

class DEANEvolutionOperator(BaseOperator):
    """
    Triggers evolution for a population of agents.
    """
    
    template_fields = ['agent_ids', 'generations', 'token_budget']
    ui_color = '#2196F3'
    
    @apply_defaults
    def __init__(
        self,
        agent_ids: Optional[List[str]] = None,
        generations: int = 5,
        token_budget: int = 10000,
        ca_rules: Optional[List[int]] = None,
        indexagent_url: str = "http://indexagent:8081",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.agent_ids = agent_ids
        self.generations = generations
        self.token_budget = token_budget
        self.ca_rules = ca_rules or [110, 30, 90, 184]
        self.indexagent_url = indexagent_url
    
    def execute(self, context):
        """Execute evolution operation."""
        # Get agent IDs from XCom if not provided
        if not self.agent_ids:
            self.agent_ids = context['task_instance'].xcom_pull(
                key='evolution_candidates'
            )
        
        if not self.agent_ids:
            self.log.warning("No agents to evolve")
            return {'evolved': 0}
        
        evolved_count = 0
        evolution_results = []
        
        # Evolve each agent
        for agent_id in self.agent_ids[:10]:  # Limit to 10 agents
            try:
                evolution_params = {
                    "generations": self.generations,
                    "mutation_rate": 0.1,
                    "crossover_rate": 0.25,
                    "ca_rules": self.ca_rules,
                    "token_budget": self.token_budget // len(self.agent_ids)
                }
                
                response = requests.post(
                    f"{self.indexagent_url}/api/v1/agents/{agent_id}/evolve",
                    json=evolution_params,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    evolution_results.append({
                        'agent_id': agent_id,
                        'success': True,
                        'generations_completed': result.get('generations', 0),
                        'fitness_improvement': result.get('fitness_improvement', 0)
                    })
                    evolved_count += 1
                else:
                    self.log.error(f"Evolution failed for agent {agent_id}: {response.text}")
                    evolution_results.append({
                        'agent_id': agent_id,
                        'success': False,
                        'error': response.text
                    })
                    
            except Exception as e:
                self.log.error(f"Exception evolving agent {agent_id}: {str(e)}")
                evolution_results.append({
                    'agent_id': agent_id,
                    'success': False,
                    'error': str(e)
                })
        
        self.log.info(f"Evolution complete: {evolved_count}/{len(self.agent_ids)} agents evolved")
        
        return {
            'evolved': evolved_count,
            'total': len(self.agent_ids),
            'results': evolution_results
        }

class DEANPatternPropagationOperator(BaseOperator):
    """
    Propagates discovered patterns across agent population.
    """
    
    template_fields = ['pattern_ids', 'target_agent_ids']
    ui_color = '#FF9800'
    
    @apply_defaults
    def __init__(
        self,
        pattern_ids: Optional[List[str]] = None,
        target_agent_ids: Optional[List[str]] = None,
        propagation_strategy: str = "fitness_weighted",
        max_recipients: int = 10,
        dean_orchestrator_url: str = "http://dean-orchestrator:8082",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.pattern_ids = pattern_ids
        self.target_agent_ids = target_agent_ids
        self.propagation_strategy = propagation_strategy
        self.max_recipients = max_recipients
        self.dean_orchestrator_url = dean_orchestrator_url
    
    def execute(self, context):
        """Execute pattern propagation."""
        # Get pattern IDs from XCom if not provided
        if not self.pattern_ids:
            patterns = context['task_instance'].xcom_pull(
                key='discovered_patterns'
            )
            if patterns:
                self.pattern_ids = [p.get('id') for p in patterns[:5]]
        
        if not self.pattern_ids:
            self.log.info("No patterns to propagate")
            return {'propagated': 0}
        
        propagation_request = {
            "pattern_ids": self.pattern_ids,
            "target_agent_ids": self.target_agent_ids,
            "propagation_strategy": self.propagation_strategy,
            "max_recipients": self.max_recipients
        }
        
        try:
            response = requests.post(
                f"{self.dean_orchestrator_url}/api/v1/patterns/propagate",
                json=propagation_request,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self.log.info(
                    f"Propagated {result.get('patterns_propagated', 0)} patterns "
                    f"to {result.get('recipients', 0)} agents"
                )
                return result
            else:
                raise AirflowException(f"Pattern propagation failed: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise AirflowException(f"Network error during pattern propagation: {str(e)}")

class DEANDiversityEnforcementOperator(BaseOperator):
    """
    Enforces genetic diversity in agent population.
    """
    
    template_fields = ['min_diversity_threshold']
    ui_color = '#9C27B0'
    
    @apply_defaults
    def __init__(
        self,
        min_diversity_threshold: float = 0.3,
        intervention_strategy: str = "mutation_injection",
        indexagent_url: str = "http://indexagent:8081",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.min_diversity_threshold = min_diversity_threshold
        self.intervention_strategy = intervention_strategy
        self.indexagent_url = indexagent_url
    
    def execute(self, context):
        """Execute diversity enforcement."""
        # Get current population
        response = requests.get(f"{self.indexagent_url}/api/v1/agents")
        agents = response.json().get('agents', [])
        active_agents = [a for a in agents if a.get('status') == 'active']
        
        if len(active_agents) < 2:
            self.log.info("Too few agents for diversity enforcement")
            return {'intervention_applied': False}
        
        # Check diversity
        agent_ids = [a['id'] for a in active_agents[:20]]
        diversity_response = requests.post(
            f"{self.indexagent_url}/api/v1/diversity/population",
            json={'population_ids': agent_ids}
        )
        
        diversity_data = diversity_response.json()
        current_diversity = diversity_data.get('diversity_score', 0)
        
        self.log.info(f"Current population diversity: {current_diversity:.3f}")
        
        if current_diversity < self.min_diversity_threshold:
            self.log.warning(f"Low diversity detected: {current_diversity:.3f}")
            
            # Apply intervention
            intervention_request = {
                "population_ids": agent_ids,
                "intervention_type": self.intervention_strategy,
                "target_diversity": self.min_diversity_threshold
            }
            
            intervention_response = requests.post(
                f"{self.indexagent_url}/api/v1/diversity/intervene",
                json=intervention_request
            )
            
            if intervention_response.status_code == 200:
                result = intervention_response.json()
                self.log.info(f"Diversity intervention applied: {result}")
                return {
                    'intervention_applied': True,
                    'diversity_before': current_diversity,
                    'actions_taken': result.get('actions_taken', [])
                }
        
        return {
            'intervention_applied': False,
            'current_diversity': current_diversity
        }

class DEANTokenBudgetOperator(BaseOperator):
    """
    Manages token budget allocation and monitoring.
    """
    
    template_fields = ['allocation_amount', 'agent_ids']
    ui_color = '#FFC107'
    
    @apply_defaults
    def __init__(
        self,
        operation: str = "check",  # check, allocate, or rebalance
        allocation_amount: Optional[int] = None,
        agent_ids: Optional[List[str]] = None,
        evolution_api_url: str = "http://dean-api:8091",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.operation = operation
        self.allocation_amount = allocation_amount
        self.agent_ids = agent_ids
        self.evolution_api_url = evolution_api_url
    
    def execute(self, context):
        """Execute token budget operation."""
        if self.operation == "check":
            return self._check_budget()
        elif self.operation == "allocate":
            return self._allocate_tokens()
        elif self.operation == "rebalance":
            return self._rebalance_tokens()
        else:
            raise AirflowException(f"Unknown operation: {self.operation}")
    
    def _check_budget(self):
        """Check current token budget status."""
        response = requests.get(f"{self.evolution_api_url}/api/v1/economy/budget")
        
        if response.status_code == 200:
            budget_data = response.json()
            self.log.info(f"Token budget status: {json.dumps(budget_data, indent=2)}")
            
            # Alert if budget is low
            if budget_data.get('available', 0) < budget_data.get('total', 1) * 0.1:
                self.log.warning("Token budget running low!")
            
            return budget_data
        else:
            raise AirflowException(f"Failed to check budget: {response.text}")
    
    def _allocate_tokens(self):
        """Allocate tokens to agents."""
        if not self.agent_ids or not self.allocation_amount:
            raise AirflowException("agent_ids and allocation_amount required for allocation")
        
        allocations = []
        for agent_id in self.agent_ids:
            allocation_request = {
                "agent_id": agent_id,
                "requested_tokens": self.allocation_amount,
                "priority": "normal"
            }
            
            response = requests.post(
                f"{self.evolution_api_url}/api/v1/economy/allocate",
                json=allocation_request
            )
            
            if response.status_code == 200:
                result = response.json()
                allocations.append({
                    'agent_id': agent_id,
                    'allocated': result.get('allocated_tokens', 0),
                    'success': True
                })
            else:
                allocations.append({
                    'agent_id': agent_id,
                    'allocated': 0,
                    'success': False,
                    'error': response.text
                })
        
        return {'allocations': allocations}
    
    def _rebalance_tokens(self):
        """Rebalance tokens across population."""
        # This would implement logic to redistribute tokens
        # from inactive/low-performing agents to active ones
        self.log.info("Token rebalancing not yet implemented")
        return {'rebalanced': False}

class DEANMonitoringOperator(BaseOperator):
    """
    Collects and reports DEAN system metrics.
    """
    
    ui_color = '#607D8B'
    
    @apply_defaults
    def __init__(
        self,
        metrics_to_collect: List[str] = None,
        dean_orchestrator_url: str = "http://dean-orchestrator:8082",
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.metrics_to_collect = metrics_to_collect or [
            'population_status',
            'token_usage',
            'pattern_discovery',
            'evolution_progress'
        ]
        self.dean_orchestrator_url = dean_orchestrator_url
    
    def execute(self, context):
        """Collect system metrics."""
        metrics = {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics': {}
        }
        
        # Collect population status
        if 'population_status' in self.metrics_to_collect:
            response = requests.get(
                f"{self.dean_orchestrator_url}/api/v1/population/status"
            )
            if response.status_code == 200:
                metrics['metrics']['population_status'] = response.json()
        
        # Collect service health
        response = requests.get(
            f"{self.dean_orchestrator_url}/api/v1/services/status"
        )
        if response.status_code == 200:
            metrics['metrics']['services'] = response.json()
        
        # Log metrics
        self.log.info(f"Collected metrics: {json.dumps(metrics, indent=2)}")
        
        # Push to monitoring system
        # In production, this would send to Prometheus/Grafana
        
        return metrics