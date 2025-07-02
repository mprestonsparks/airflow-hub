"""
DEAN API Hook for Airflow

Provides connection and interaction capabilities with the DEAN Agent Evolution Service.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

import requests
from airflow.hooks.base import BaseHook
from airflow.exceptions import AirflowException

logger = logging.getLogger(__name__)

class DeanApiHook(BaseHook):
    """
    Hook for interacting with DEAN Agent Evolution Service API.
    
    This hook provides methods to:
    - Create and manage agents
    - Trigger evolution processes
    - Monitor population statistics
    - Retrieve patterns and insights
    """
    
    conn_name_attr = "dean_api_conn_id"
    default_conn_name = "dean_api_default"
    conn_type = "HTTP"
    hook_name = "DEAN API"
    
    def __init__(self, dean_api_conn_id: str = default_conn_name, timeout: int = 30):
        super().__init__()
        self.dean_api_conn_id = dean_api_conn_id
        self.timeout = timeout
        self._base_url = None
        self._session = None
    
    @property
    def base_url(self) -> str:
        """Get the base URL for DEAN API."""
        if self._base_url is None:
            conn = self.get_connection(self.dean_api_conn_id)
            # Require connection to be configured - no hardcoded defaults
            if not conn.host:
                raise AirflowException(
                    f"No host configured for connection '{self.dean_api_conn_id}'. "
                    "Please configure the DEAN API connection in Airflow."
                )
            else:
                schema = conn.schema or "http"
                port = f":{conn.port}" if conn.port else ""
                self._base_url = f"{schema}://{conn.host}{port}"
        return self._base_url
    
    @property
    def session(self) -> requests.Session:
        """Get HTTP session with default configuration."""
        if self._session is None:
            self._session = requests.Session()
            self._session.timeout = self.timeout
            
            # Add authentication if configured
            conn = self.get_connection(self.dean_api_conn_id)
            if conn.login and conn.password:
                self._session.auth = (conn.login, conn.password)
            elif conn.password:  # API key in password field
                self._session.headers.update({
                    "Authorization": f"Bearer {conn.password}"
                })
        return self._session
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to DEAN API."""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"DEAN API request failed: {method} {url} - {e}")
            raise AirflowException(f"Failed to communicate with DEAN API: {e}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from DEAN API: {e}")
            raise AirflowException(f"Invalid response from DEAN API: {e}")
    
    def health_check(self) -> Dict[str, Any]:
        """Check DEAN service health."""
        return self._make_request("GET", "/health")
    
    def create_agent(self, 
                    goal: str, 
                    token_budget: int = 1000,
                    agent_id: Optional[str] = None,
                    specialized_domain: Optional[str] = None,
                    diversity_weight: float = 0.3) -> Dict[str, Any]:
        """Create a new agent."""
        payload = {
            "goal": goal,
            "token_budget": token_budget,
            "diversity_weight": diversity_weight
        }
        
        if agent_id:
            payload["agent_id"] = agent_id
        if specialized_domain:
            payload["specialized_domain"] = specialized_domain
            
        return self._make_request("POST", "/agents", json=payload)
    
    def create_population(self,
                         population_size: int,
                         base_goal: str,
                         base_token_budget: int = 1000,
                         diversity_factor: float = 0.3) -> List[Dict[str, Any]]:
        """Create a population of agents."""
        payload = {
            "population_size": population_size,
            "base_goal": base_goal,
            "base_token_budget": base_token_budget,
            "diversity_factor": diversity_factor
        }
        
        return self._make_request("POST", "/populations", json=payload)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all active agents."""
        return self._make_request("GET", "/agents")
    
    def get_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get details of a specific agent."""
        return self._make_request("GET", f"/agents/{agent_id}")
    
    def evolve_agent(self, 
                     agent_id: str,
                     cycles: int = 1,
                     environment: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Trigger evolution for a specific agent."""
        payload = {
            "agent_id": agent_id,
            "cycles": cycles,
            "environment": environment or {}
        }
        
        return self._make_request("POST", f"/agents/{agent_id}/evolve", json=payload)
    
    def evolve_population(self, cycles: int = 1) -> Dict[str, Any]:
        """Trigger population-wide evolution."""
        params = {"cycles": cycles}
        return self._make_request("POST", "/population/evolve", params=params)
    
    def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        """Delete an agent and cleanup resources."""
        return self._make_request("DELETE", f"/agents/{agent_id}")
    
    def get_population_stats(self) -> Dict[str, Any]:
        """Get population-wide statistics."""
        return self._make_request("GET", "/population/stats")
    
    def wait_for_service(self, max_retries: int = 30, retry_delay: int = 2) -> bool:
        """Wait for DEAN service to become available."""
        import time
        
        for attempt in range(max_retries):
            try:
                health = self.health_check()
                if health.get("status") == "healthy":
                    logger.info("DEAN service is healthy and ready")
                    return True
            except Exception as e:
                logger.warning(f"DEAN service not ready (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        
        logger.error(f"DEAN service failed to become ready after {max_retries} attempts")
        return False