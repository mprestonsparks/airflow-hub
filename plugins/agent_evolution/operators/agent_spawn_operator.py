"""
Agent Spawn Operator for DEAN system.
Custom Airflow operator for spawning DEAN agents with economic constraints.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.exceptions import AirflowException
from airflow.hooks.base import BaseHook
from airflow.models import Variable

logger = logging.getLogger(__name__)

class AgentSpawnOperator(BaseOperator):
    """
    Spawns DEAN agents with economic constraints via IndexAgent API.
    
    This operator creates a population of agents with specified parameters,
    managing token budgets and diversity requirements.
    """
    
    template_fields = ['population_size', 'base_goal', 'base_token_budget']
    
    @apply_defaults
    def __init__(
        self,
        population_size: int,
        base_goal: str = "Optimize code efficiency",
        base_token_budget: int = 1000,
        diversity_threshold: float = 0.3,
        max_concurrent_agents: int = 10,
        indexagent_conn_id: str = "indexagent_api",
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.population_size = population_size
        self.base_goal = base_goal
        self.base_token_budget = base_token_budget
        self.diversity_threshold = diversity_threshold
        self.max_concurrent_agents = max_concurrent_agents
        self.indexagent_conn_id = indexagent_conn_id
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent spawning operation."""
        logger.info(f"Starting agent spawn operation: {self.population_size} agents")
        
        # Get IndexAgent API connection
        api_url = self._get_api_url()
        
        # Check current agent population
        current_agents = self._get_current_agents(api_url)
        
        if len(current_agents) >= self.max_concurrent_agents:
            logger.warning(f"Max concurrent agents ({self.max_concurrent_agents}) reached")
            return {
                "spawned_agents": 0,
                "reason": "max_concurrent_limit_reached",
                "current_population": len(current_agents)
            }
        
        # Calculate how many agents to spawn
        available_slots = self.max_concurrent_agents - len(current_agents)
        agents_to_spawn = min(self.population_size, available_slots)
        
        # Check global token budget
        budget_status = self._check_global_budget(api_url)
        if not budget_status["budget_available"]:
            raise AirflowException("Insufficient global token budget for agent spawning")
        
        # Spawn agents
        spawned_agents = []
        for i in range(agents_to_spawn):
            try:
                agent_config = self._create_agent_config(i, context)
                agent = self._spawn_single_agent(api_url, agent_config)
                spawned_agents.append(agent)
                logger.info(f"Spawned agent {i+1}/{agents_to_spawn}: {agent['id']}")
            
            except Exception as e:
                logger.error(f"Failed to spawn agent {i+1}: {e}")
                # Continue with other agents
        
        result = {
            "spawned_agents": len(spawned_agents),
            "agent_ids": [agent["id"] for agent in spawned_agents],
            "total_tokens_allocated": sum(agent.get("token_budget", {}).get("total", 0) for agent in spawned_agents),
            "population_diversity": self._calculate_population_diversity(spawned_agents),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Agent spawn operation completed: {result}")
        return result
    
    def _get_api_url(self) -> str:
        """Get IndexAgent API URL from connection or variable."""
        try:
            # Try to get from Airflow connection
            conn = BaseHook.get_connection(self.indexagent_conn_id)
            return f"http://{conn.host}:{conn.port}"
        except:
            # Fallback to variable or default
            return Variable.get("INDEXAGENT_API_URL", "http://indexagent:8081")
    
    def _get_current_agents(self, api_url: str) -> List[Dict[str, Any]]:
        """Get current agent population from IndexAgent API."""
        try:
            response = requests.get(f"{api_url}/api/v1/agents", timeout=30)
            response.raise_for_status()
            return response.json().get("agents", [])
        except Exception as e:
            logger.warning(f"Failed to get current agents: {e}")
            return []
    
    def _check_global_budget(self, api_url: str) -> Dict[str, Any]:
        """Check global token budget availability."""
        try:
            response = requests.get(f"{api_url}/api/v1/budget/global", timeout=30)
            response.raise_for_status()
            budget_data = response.json()
            
            required_tokens = self.population_size * self.base_token_budget
            available_tokens = budget_data.get("available_tokens", 0)
            
            return {
                "budget_available": available_tokens >= required_tokens,
                "available_tokens": available_tokens,
                "required_tokens": required_tokens
            }
        except Exception as e:
            logger.warning(f"Failed to check global budget: {e}")
            # Assume budget is available if we can't check
            return {"budget_available": True}
    
    def _create_agent_config(self, agent_index: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create configuration for a single agent."""
        # Add diversity to agent goals and parameters
        diversity_factor = (agent_index * 0.1) % 0.5  # 0.0 to 0.4
        
        return {
            "goal": f"{self.base_goal} (Agent {agent_index + 1})",
            "token_budget": int(self.base_token_budget * (1.0 + diversity_factor)),
            "diversity_weight": self.diversity_threshold + diversity_factor,
            "specialized_domain": self._get_specialized_domain(agent_index),
            "agent_metadata": {
                "spawn_batch": context.get("run_id"),
                "spawn_index": agent_index,
                "spawn_timestamp": datetime.utcnow().isoformat()
            }
        }
    
    def _get_specialized_domain(self, agent_index: int) -> Optional[str]:
        """Assign specialized domain based on agent index."""
        domains = [
            "code_optimization",
            "pattern_detection", 
            "resource_efficiency",
            "collaboration",
            "meta_learning"
        ]
        return domains[agent_index % len(domains)]
    
    def _spawn_single_agent(self, api_url: str, agent_config: Dict[str, Any]) -> Dict[str, Any]:
        """Spawn a single agent via API."""
        response = requests.post(
            f"{api_url}/api/v1/agents",
            json=agent_config,
            timeout=60
        )
        response.raise_for_status()
        return response.json()
    
    def _calculate_population_diversity(self, agents: List[Dict[str, Any]]) -> float:
        """Calculate diversity score for spawned population."""
        if len(agents) <= 1:
            return 1.0
        
        # Simple diversity calculation based on token budgets and domains
        token_budgets = [agent.get("token_budget", {}).get("total", 0) for agent in agents]
        domains = [agent.get("specialized_domain") for agent in agents]
        
        # Token budget diversity (coefficient of variation)
        if token_budgets and max(token_budgets) > 0:
            avg_budget = sum(token_budgets) / len(token_budgets)
            budget_variance = sum((b - avg_budget) ** 2 for b in token_budgets) / len(token_budgets)
            budget_diversity = (budget_variance ** 0.5) / avg_budget if avg_budget > 0 else 0
        else:
            budget_diversity = 0
        
        # Domain diversity (unique domains / total agents)
        unique_domains = len(set(d for d in domains if d))
        domain_diversity = unique_domains / len(agents) if agents else 0
        
        # Combined diversity score
        return (budget_diversity + domain_diversity) / 2