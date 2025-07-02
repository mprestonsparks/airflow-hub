"""
Agent Evolution Operator for DEAN system.
Custom Airflow operator for triggering agent evolution cycles.

Implements FR-028: Enhanced Airflow Integration with economic constraint
enforcement at the orchestration layer and multi-agent workflow orchestration.
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

class AgentEvolutionOperator(BaseOperator):
    """
    Triggers evolution cycles for DEAN agent population with economic constraints.
    
    Implements FR-028: Enhanced Airflow Integration
    - Economic constraint enforcement at orchestration layer
    - Multi-agent workflow orchestration with token budget validation
    - Population initialization and evolution execution
    - Pattern propagation across agent populations
    - Integration with service communication contracts
    """
    
    template_fields = ['generations', 'mutation_rate', 'crossover_rate', 'population_budget', 'child_budget_ratio']
    
    @apply_defaults
    def __init__(
        self,
        generations: int = 10,
        mutation_rate: float = 0.1,
        crossover_rate: float = 0.7,
        diversity_threshold: float = 0.3,
        max_parallel_evolutions: int = 4,
        evolution_timeout: int = 300,
        population_budget: int = 100000,  # Total token budget for population
        child_budget_ratio: float = 0.5,   # Child agent budget as ratio of parent
        min_agent_budget: int = 1024,      # Minimum budget for viable agent
        budget_reserve_ratio: float = 0.2, # Reserve budget for emergencies
        economic_enforcement: bool = True,  # Enable economic constraints
        indexagent_conn_id: str = "indexagent_api",
        evolution_conn_id: str = "evolution_api",
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.diversity_threshold = diversity_threshold
        self.max_parallel_evolutions = max_parallel_evolutions
        self.evolution_timeout = evolution_timeout
        self.population_budget = population_budget
        self.child_budget_ratio = child_budget_ratio
        self.min_agent_budget = min_agent_budget
        self.budget_reserve_ratio = budget_reserve_ratio
        self.economic_enforcement = economic_enforcement
        self.indexagent_conn_id = indexagent_conn_id
        self.evolution_conn_id = evolution_conn_id
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent evolution operation with economic constraints.
        
        Implements FR-028 multi-agent workflow orchestration with:
        - Economic constraint validation before evolution
        - Population initialization if needed
        - Pattern propagation across populations
        - Token budget management throughout evolution
        """
        logger.info(f"Starting FR-028 enhanced evolution cycle: {self.generations} generations")
        
        # Get API connections
        indexagent_url = self._get_indexagent_url()
        evolution_url = self._get_evolution_url()
        
        # Validate economic constraints before starting
        if self.economic_enforcement:
            economic_validation = self._validate_economic_constraints(indexagent_url, evolution_url)
            if not economic_validation["valid"]:
                logger.error(f"Economic constraint validation failed: {economic_validation['reason']}")
                return {
                    "evolved_agents": 0,
                    "reason": "economic_constraints_violated",
                    "economic_validation": economic_validation,
                    "generations_completed": 0
                }
            logger.info(f"Economic constraints validated: {economic_validation}")
        
        # Get current agent population
        population = self._get_agent_population(indexagent_url)
        
        # Initialize population if empty or insufficient
        if not population or len(population) < 2:
            logger.info("Initializing population for evolution")
            population_init_result = self._initialize_population(indexagent_url, evolution_url)
            population = self._get_agent_population(indexagent_url)
            logger.info(f"Population initialized: {len(population)} agents created")
        
        if not population:
            logger.warning("No agents available after initialization attempt")
            return {
                "evolved_agents": 0,
                "reason": "population_initialization_failed",
                "generations_completed": 0
            }
        
        logger.info(f"Found {len(population)} agents for evolution")
        
        # Check population diversity before evolution
        initial_diversity = self._check_population_diversity(evolution_url, population)
        
        # Apply diversity enforcement if needed
        if initial_diversity < self.diversity_threshold:
            diversity_result = self._enforce_diversity(evolution_url, population)
            logger.info(f"Diversity enforcement applied: {diversity_result}")
        
        # Execute evolution cycles
        evolution_results = []
        
        for generation in range(self.generations):
            logger.info(f"Starting evolution generation {generation + 1}/{self.generations}")
            
            try:
                # Trigger evolution for all agents
                gen_result = self._evolve_generation(
                    indexagent_url, evolution_url, population, generation
                )
                evolution_results.append(gen_result)
                
                # Update population with evolved agents
                population = self._get_agent_population(indexagent_url)
                
                # Check if early termination criteria met
                if self._should_terminate_early(evolution_results):
                    logger.info(f"Early termination at generation {generation + 1}")
                    break
                    
            except Exception as e:
                logger.error(f"Evolution failed at generation {generation + 1}: {e}")
                break
        
        # Calculate final results
        final_diversity = self._check_population_diversity(evolution_url, population)
        
        result = {
            "evolved_agents": len(population),
            "generations_completed": len(evolution_results),
            "initial_diversity": initial_diversity,
            "final_diversity": final_diversity,
            "diversity_improvement": final_diversity - initial_diversity,
            "evolution_results": evolution_results,
            "population_stats": self._get_population_stats(evolution_url),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Evolution cycle completed: {result}")
        return result
    
    def _get_indexagent_url(self) -> str:
        """Get IndexAgent API URL."""
        try:
            conn = BaseHook.get_connection(self.indexagent_conn_id)
            return f"http://{conn.host}:{conn.port}"
        except:
            return Variable.get("INDEXAGENT_API_URL", "http://indexagent:8081")
    
    def _get_evolution_url(self) -> str:
        """Get Evolution API URL."""
        try:
            conn = BaseHook.get_connection(self.evolution_conn_id)
            return f"http://{conn.host}:{conn.port}"
        except:
            return Variable.get("EVOLUTION_API_URL", "http://agent-evolution:8090")
    
    def _get_agent_population(self, api_url: str) -> List[Dict[str, Any]]:
        """Get current agent population."""
        try:
            response = requests.get(f"{api_url}/api/v1/agents", timeout=30)
            response.raise_for_status()
            return response.json().get("agents", [])
        except Exception as e:
            logger.error(f"Failed to get agent population: {e}")
            return []
    
    def _check_population_diversity(self, evolution_url: str, population: List[Dict[str, Any]]) -> float:
        """Check current population diversity score."""
        try:
            response = requests.post(
                f"{evolution_url}/api/v1/diversity/calculate",
                json={"agent_ids": [agent["id"] for agent in population]},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("diversity_score", 0.0)
        except Exception as e:
            logger.warning(f"Failed to check diversity: {e}")
            return 0.5  # Assume moderate diversity
    
    def _enforce_diversity(self, evolution_url: str, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply diversity enforcement to population."""
        try:
            response = requests.post(
                f"{evolution_url}/api/v1/diversity/enforce",
                json={
                    "agent_ids": [agent["id"] for agent in population],
                    "target_diversity": self.diversity_threshold
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to enforce diversity: {e}")
            return {"actions_taken": [], "error": str(e)}
    
    def _evolve_generation(self, indexagent_url: str, evolution_url: str, 
                          population: List[Dict[str, Any]], generation: int) -> Dict[str, Any]:
        """Evolve a single generation of agents."""
        
        # Apply cellular automata evolution
        ca_result = self._apply_cellular_automata(evolution_url, population, generation)
        
        # Trigger individual agent evolution
        individual_results = []
        for agent in population[:self.max_parallel_evolutions]:  # Limit parallel evolutions
            try:
                result = self._evolve_individual_agent(indexagent_url, agent["id"])
                individual_results.append(result)
            except Exception as e:
                logger.warning(f"Failed to evolve agent {agent['id']}: {e}")
        
        # Detect emergent patterns
        pattern_results = self._detect_emergent_patterns(evolution_url, population)
        
        # Propagate discovered patterns across populations (FR-028)
        propagation_results = {"patterns_propagated": 0}
        if pattern_results.get("new_patterns"):
            propagation_results = self._propagate_patterns_across_populations(
                evolution_url, pattern_results["new_patterns"]
            )
        
        # Apply DSPy optimization
        optimization_results = self._apply_dspy_optimization(evolution_url, population)
        
        # Validate economic constraints during evolution
        if self.economic_enforcement:
            post_evolution_budget = self._check_post_evolution_budget(indexagent_url, population)
        else:
            post_evolution_budget = {"sufficient": True}
        
        return {
            "generation": generation,
            "cellular_automata_result": ca_result,
            "individual_evolutions": len(individual_results),
            "successful_evolutions": len([r for r in individual_results if r.get("success", False)]),
            "patterns_detected": len(pattern_results.get("new_patterns", [])),
            "patterns_propagated": propagation_results.get("patterns_propagated", 0),
            "pattern_propagation_success_rate": propagation_results.get("success_rate", 0),
            "optimizations_applied": optimization_results.get("optimizations_applied", 0),
            "budget_status": post_evolution_budget,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _apply_cellular_automata(self, evolution_url: str, population: List[Dict[str, Any]], 
                               generation: int) -> Dict[str, Any]:
        """Apply cellular automata rules to population."""
        try:
            response = requests.post(
                f"{evolution_url}/api/v1/cellular-automata/evolve",
                json={
                    "agent_ids": [agent["id"] for agent in population],
                    "generation": generation,
                    "mutation_rate": self.mutation_rate,
                    "crossover_rate": self.crossover_rate
                },
                timeout=self.evolution_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Cellular automata evolution failed: {e}")
            return {"rule_applications": [], "error": str(e)}
    
    def _evolve_individual_agent(self, indexagent_url: str, agent_id: str) -> Dict[str, Any]:
        """Trigger evolution for a single agent."""
        try:
            response = requests.post(
                f"{indexagent_url}/api/v1/agents/{agent_id}/evolve",
                json={
                    "mutation_rate": self.mutation_rate,
                    "crossover_rate": self.crossover_rate
                },
                timeout=self.evolution_timeout
            )
            response.raise_for_status()
            result = response.json()
            result["success"] = True
            return result
        except Exception as e:
            logger.warning(f"Individual evolution failed for {agent_id}: {e}")
            return {"success": False, "error": str(e), "agent_id": agent_id}
    
    def _detect_emergent_patterns(self, evolution_url: str, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect emergent patterns in agent behavior."""
        try:
            response = requests.post(
                f"{evolution_url}/api/v1/patterns/detect",
                json={
                    "agent_ids": [agent["id"] for agent in population],
                    "analysis_window": "current_generation"
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Pattern detection failed: {e}")
            return {"new_patterns": [], "error": str(e)}
    
    def _apply_dspy_optimization(self, evolution_url: str, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply DSPy optimization to population."""
        try:
            response = requests.post(
                f"{evolution_url}/api/v1/dspy/optimize",
                json={
                    "agent_ids": [agent["id"] for agent in population],
                    "optimization_type": "population_meta_learning"
                },
                timeout=self.evolution_timeout
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"DSPy optimization failed: {e}")
            return {"optimizations_applied": 0, "error": str(e)}
    
    def _get_population_stats(self, evolution_url: str) -> Dict[str, Any]:
        """Get comprehensive population statistics."""
        try:
            response = requests.get(f"{evolution_url}/api/v1/population/stats", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Failed to get population stats: {e}")
            return {"error": str(e)}
    
    def _should_terminate_early(self, evolution_results: List[Dict[str, Any]]) -> bool:
        """Check if evolution should terminate early."""
        if len(evolution_results) < 3:
            return False
        
        # Check for convergence (no improvements in last 3 generations)
        recent_successes = [
            result.get("successful_evolutions", 0) 
            for result in evolution_results[-3:]
        ]
        
        # Terminate if no successful evolutions in recent generations
        if sum(recent_successes) == 0:
            logger.info("Early termination: no successful evolutions in recent generations")
            return True
        
        # Check for pattern detection plateau
        recent_patterns = [
            result.get("patterns_detected", 0)
            for result in evolution_results[-3:]
        ]
        
        if max(recent_patterns) == 0:
            logger.info("Early termination: no new patterns detected recently")
            return True
        
        return False
    
    def _validate_economic_constraints(self, indexagent_url: str, evolution_url: str) -> Dict[str, Any]:
        """
        Validate economic constraints before evolution per FR-028.
        
        Checks:
        - Population budget sufficient for evolution cycles
        - Individual agent budgets meet minimum requirements
        - Reserve budget available for unexpected costs
        - Token transaction history for budget validation
        """
        try:
            # Get current population budget usage
            budget_response = requests.get(
                f"{indexagent_url}/api/v1/economy/population-budget",
                timeout=30
            )
            budget_response.raise_for_status()
            budget_data = budget_response.json()
            
            current_usage = budget_data.get("total_allocated", 0)
            available_budget = self.population_budget - current_usage
            reserve_budget = self.population_budget * self.budget_reserve_ratio
            
            # Calculate estimated evolution cost
            population = self._get_agent_population(indexagent_url)
            estimated_cost = self._estimate_evolution_cost(population)
            
            # Validate constraints
            if available_budget < estimated_cost + reserve_budget:
                return {
                    "valid": False,
                    "reason": "insufficient_budget",
                    "details": {
                        "available_budget": available_budget,
                        "estimated_cost": estimated_cost,
                        "reserve_budget": reserve_budget,
                        "required_budget": estimated_cost + reserve_budget
                    }
                }
            
            # Check individual agent budgets
            low_budget_agents = [
                agent for agent in population 
                if agent.get("token_budget", 0) < self.min_agent_budget
            ]
            
            if len(low_budget_agents) > len(population) * 0.5:  # More than 50% low budget
                return {
                    "valid": False,
                    "reason": "too_many_low_budget_agents",
                    "details": {
                        "low_budget_agents": len(low_budget_agents),
                        "total_agents": len(population),
                        "percentage": len(low_budget_agents) / len(population) * 100
                    }
                }
            
            return {
                "valid": True,
                "available_budget": available_budget,
                "estimated_cost": estimated_cost,
                "budget_utilization": current_usage / self.population_budget,
                "low_budget_agents": len(low_budget_agents)
            }
            
        except Exception as e:
            logger.error(f"Economic constraint validation failed: {e}")
            return {
                "valid": False,
                "reason": "validation_error",
                "error": str(e)
            }
    
    def _estimate_evolution_cost(self, population: List[Dict[str, Any]]) -> int:
        """Estimate token cost for evolution cycles."""
        base_cost_per_agent = 1000  # Base tokens for evolution operations
        ca_cost_per_generation = 500  # Cellular automata cost
        pattern_detection_cost = 200 * len(population)  # Pattern detection
        
        total_cost = (
            len(population) * base_cost_per_agent * self.generations +
            ca_cost_per_generation * self.generations +
            pattern_detection_cost
        )
        
        return int(total_cost * 1.2)  # 20% buffer
    
    def _initialize_population(self, indexagent_url: str, evolution_url: str) -> Dict[str, Any]:
        """
        Initialize agent population for evolution per FR-028.
        
        Creates initial population with:
        - Diverse agent configurations
        - Balanced token budgets
        - Foundational strategies for evolution
        """
        try:
            # Calculate individual agent budgets
            min_population_size = 4
            agent_budget = min(
                self.population_budget // (min_population_size * 2),  # Reserve half budget
                self.population_budget * 0.1  # Max 10% per agent
            )
            
            if agent_budget < self.min_agent_budget:
                logger.warning(f"Calculated agent budget {agent_budget} below minimum {self.min_agent_budget}")
                agent_budget = self.min_agent_budget
            
            # Create diverse initial agents
            initial_agents = []
            agent_templates = [
                {"strategy": "exploration", "efficiency": 0.6, "creativity": 0.8},
                {"strategy": "optimization", "efficiency": 0.9, "creativity": 0.4},
                {"strategy": "learning", "efficiency": 0.7, "creativity": 0.7},
                {"strategy": "collaboration", "efficiency": 0.5, "creativity": 0.9}
            ]
            
            for i, template in enumerate(agent_templates):
                agent_data = {
                    "name": f"initial_agent_{i+1}",
                    "token_budget": agent_budget,
                    "generation": 0,
                    "parent_id": None,
                    "traits": template,
                    "strategies": [template["strategy"]]
                }
                
                response = requests.post(
                    f"{indexagent_url}/api/v1/agents",
                    json=agent_data,
                    timeout=30
                )
                
                if response.status_code == 201:
                    initial_agents.append(response.json())
                    logger.info(f"Created initial agent: {agent_data['name']}")
                else:
                    logger.warning(f"Failed to create agent {agent_data['name']}: {response.status_code}")
            
            return {
                "agents_created": len(initial_agents),
                "total_budget_allocated": len(initial_agents) * agent_budget,
                "agent_budget": agent_budget,
                "created_agents": initial_agents
            }
            
        except Exception as e:
            logger.error(f"Population initialization failed: {e}")
            return {
                "agents_created": 0,
                "error": str(e)
            }
    
    def _propagate_patterns_across_populations(self, evolution_url: str, 
                                             patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Propagate discovered patterns across agent populations per FR-028.
        
        Implements cross-population pattern sharing for knowledge transfer.
        """
        try:
            propagation_results = []
            
            for pattern in patterns:
                response = requests.post(
                    f"{evolution_url}/api/v1/patterns/propagate",
                    json={
                        "pattern_id": pattern.get("id"),
                        "pattern_type": pattern.get("type"),
                        "effectiveness_score": pattern.get("effectiveness", 0.5),
                        "source_agent_id": pattern.get("discovered_by"),
                        "pattern_data": pattern.get("data", {}),
                        "propagation_scope": "global"  # Cross-population propagation
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    propagation_results.append({
                        "pattern_id": pattern.get("id"),
                        "propagated": True,
                        "affected_agents": response.json().get("affected_agents", 0)
                    })
                else:
                    propagation_results.append({
                        "pattern_id": pattern.get("id"),
                        "propagated": False,
                        "error": f"HTTP {response.status_code}"
                    })
            
            successful_propagations = len([r for r in propagation_results if r["propagated"]])
            
            return {
                "patterns_propagated": successful_propagations,
                "total_patterns": len(patterns),
                "propagation_results": propagation_results,
                "success_rate": successful_propagations / len(patterns) if patterns else 0
            }
            
        except Exception as e:
            logger.error(f"Pattern propagation failed: {e}")
            return {
                "patterns_propagated": 0,
                "error": str(e)
            }
    
    def _check_post_evolution_budget(self, indexagent_url: str, population: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Check budget status after evolution operations."""
        try:
            budget_response = requests.get(
                f"{indexagent_url}/api/v1/economy/population-budget",
                timeout=30
            )
            budget_response.raise_for_status()
            budget_data = budget_response.json()
            
            current_usage = budget_data.get("total_allocated", 0)
            available_budget = self.population_budget - current_usage
            utilization_rate = current_usage / self.population_budget
            
            # Check if budget is critically low
            critical_threshold = self.population_budget * 0.1  # 10% remaining
            warning_threshold = self.population_budget * 0.2   # 20% remaining
            
            if available_budget < critical_threshold:
                status = "critical"
                message = "Budget critically low - evolution should be halted"
            elif available_budget < warning_threshold:
                status = "warning"
                message = "Budget low - consider reducing evolution intensity"
            else:
                status = "sufficient"
                message = "Budget adequate for continued evolution"
            
            return {
                "sufficient": status != "critical",
                "status": status,
                "message": message,
                "available_budget": available_budget,
                "utilization_rate": utilization_rate,
                "budget_remaining_percent": (available_budget / self.population_budget) * 100
            }
            
        except Exception as e:
            logger.warning(f"Failed to check post-evolution budget: {e}")
            return {
                "sufficient": True,  # Assume sufficient if check fails
                "status": "unknown",
                "error": str(e)
            }