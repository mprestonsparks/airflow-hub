#!/usr/bin/env python3
"""
Economic Governor API Client
Provides a clean interface to the Economic Governor service via REST API
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


class EconomicGovernorClient:
    """Client for interacting with the Economic Governor API"""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize the client with the API base URL"""
        if base_url is None:
            # Try to get from Airflow Variable first, then environment
            base_url = Variable.get("dean_api_url", os.environ.get("DEAN_API_URL", "http://infra-api:8091"))
        
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system-wide economic metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/economy/metrics")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get economic metrics: {e}")
            raise
    
    def get_agent_budget(self, agent_id: str) -> Dict[str, Any]:
        """Get economic status for a specific agent"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/economy/agent/{agent_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get agent budget for {agent_id}: {e}")
            raise
    
    def use_tokens(self, agent_id: str, tokens: int, action_type: str, 
                   task_success: float, quality_score: float) -> Dict[str, Any]:
        """Record token usage for an agent"""
        try:
            payload = {
                "agent_id": agent_id,
                "tokens": tokens,
                "action_type": action_type,
                "task_success": task_success,
                "quality_score": quality_score
            }
            response = self.session.post(f"{self.base_url}/api/v1/economy/use-tokens", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to record token usage for {agent_id}: {e}")
            raise
    
    def allocate_tokens(self, agent_id: str, performance: float, generation: int) -> Dict[str, Any]:
        """Allocate tokens to an agent based on performance"""
        try:
            payload = {
                "agent_id": agent_id,
                "performance": performance,
                "generation": generation
            }
            response = self.session.post(f"{self.base_url}/api/v1/economy/allocate", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to allocate tokens to {agent_id}: {e}")
            raise
    
    def rebalance_budgets(self) -> Dict[str, Any]:
        """Trigger economic rebalancing across all agents"""
        try:
            response = self.session.post(f"{self.base_url}/api/v1/economy/rebalance")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to rebalance budgets: {e}")
            raise
    
    def check_budget_allows_action(self, agent_id: str, required_tokens: int) -> bool:
        """Check if an agent has sufficient budget for an action"""
        try:
            budget_info = self.get_agent_budget(agent_id)
            remaining = budget_info["budget"]["remaining"]
            return remaining >= required_tokens
        except Exception as e:
            logger.error(f"Failed to check budget for {agent_id}: {e}")
            return False
    
    def close(self):
        """Close the HTTP session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager support"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on context exit"""
        self.close()


# Convenience functions for backward compatibility
def check_global_budget_via_api(min_budget: int = 10000) -> Dict[str, Any]:
    """Check if global budget allows new operations"""
    with EconomicGovernorClient() as client:
        metrics = client.get_system_metrics()
        available = metrics["global_budget"]["available"]
        
        return {
            "has_budget": available >= min_budget,
            "available_budget": available,
            "usage_rate": metrics["global_budget"]["usage_rate"],
            "metrics": metrics
        }


def use_tokens_via_api(agent_id: str, tokens: int, action_type: str,
                      task_success: float, quality_score: float) -> bool:
    """Use tokens via API and return success status"""
    with EconomicGovernorClient() as client:
        try:
            result = client.use_tokens(agent_id, tokens, action_type, task_success, quality_score)
            return result.get("success", False)
        except Exception:
            return False