#!/usr/bin/env python3
"""
Diversity Management API Client
"""

import os
import logging
from typing import Dict, Any, Optional, List
import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


class DiversityClient:
    """Client for diversity management via API"""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = Variable.get("dean_api_url", os.environ.get("DEAN_API_URL", "http://infra-api:8091"))
        
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def register_agent(self, agent_id: str, strategies: List[str], 
                      lineage: List[str], generation: int) -> bool:
        """Register agent with diversity tracker"""
        try:
            payload = {
                "agent_id": agent_id,
                "strategies": strategies,
                "lineage": lineage,
                "generation": generation
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/diversity/agents/register",
                json=payload
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            return False
    
    def get_diversity_metrics(self) -> Dict[str, Any]:
        """Get population diversity metrics"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/diversity/metrics")
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get diversity metrics: {e}")
            raise
    
    def check_intervention_needed(self) -> Optional[str]:
        """Check if intervention needed"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/diversity/interventions/check"
            )
            response.raise_for_status()
            return response.json().get("intervention_type")
            
        except Exception as e:
            logger.error(f"Failed to check intervention: {e}")
            return None
    
    def apply_intervention(self, agent_id: str, intervention_type: str) -> bool:
        """Apply diversity intervention"""
        try:
            payload = {
                "agent_id": agent_id,
                "intervention_type": intervention_type
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/diversity/interventions/apply",
                json=payload
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply intervention: {e}")
            return False
    
    def force_mutation(self, agent_id: str) -> bool:
        """Force mutation on agent"""
        return self.apply_intervention(agent_id, "mutation")
    
    def import_foreign_pattern(self, agent_id: str) -> bool:
        """Import foreign pattern to agent"""
        return self.apply_intervention(agent_id, "foreign_pattern")
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DiversityManager:
    """Mock wrapper for backward compatibility"""
    
    def __init__(self):
        self.client = DiversityClient()
    
    def register_agent(self, agent_id: str, strategies: List[str], 
                      lineage: List[str], generation: int):
        """Register via API"""
        return self.client.register_agent(agent_id, strategies, lineage, generation)
    
    def calculate_diversity_metrics(self) -> Dict[str, Any]:
        """Get metrics via API"""
        return self.client.get_diversity_metrics()
    
    def check_intervention_needed(self) -> Optional[str]:
        """Check via API"""
        return self.client.check_intervention_needed()
    
    def force_mutation(self, agent_id: str):
        """Apply mutation via API"""
        return self.client.force_mutation(agent_id)
    
    def import_foreign_pattern(self, agent_id: str):
        """Import pattern via API"""
        return self.client.import_foreign_pattern(agent_id)
    
    def get_diversity_report(self) -> Dict[str, Any]:
        """Get report via API"""
        metrics = self.client.get_diversity_metrics()
        return {
            "diversity_status": "healthy" if metrics.get("diversity_score", 0) > 0.3 else "low",
            "metrics": metrics
        }