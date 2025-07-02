#!/usr/bin/env python3
"""
Optimization Service API Client
"""

import os
import logging
from typing import Dict, Any, Optional, List
import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


class OptimizationClient:
    """Client for prompt optimization via API"""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = Variable.get("dean_api_url", os.environ.get("DEAN_API_URL", "http://infra-api:8091"))
        
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def optimize_prompt(self, task_description: str, 
                       performance_metrics: Dict[str, float],
                       historical_context: List[Dict] = None) -> str:
        """Optimize prompt for task"""
        try:
            payload = {
                "task_description": task_description,
                "performance_metrics": performance_metrics,
                "historical_context": historical_context or []
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/optimize/prompt",
                json=payload
            )
            response.raise_for_status()
            return response.json()["optimized_prompt"]
            
        except Exception as e:
            logger.error(f"Failed to optimize prompt: {e}")
            raise
    
    def inject_patterns(self, patterns: List[Dict[str, Any]]) -> bool:
        """Inject meta-patterns into optimizer"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/optimize/patterns/inject",
                json=patterns
            )
            response.raise_for_status()
            return True
            
        except Exception as e:
            logger.error(f"Failed to inject patterns: {e}")
            return False
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class DEANOptimizer:
    """Mock wrapper for backward compatibility"""
    
    def __init__(self):
        self.client = OptimizationClient()
    
    def optimize(self, task: str, metrics: Dict[str, float]) -> str:
        """Optimize via API"""
        return self.client.optimize_prompt(task, metrics)
    
    def inject_meta_patterns(self, patterns: List[Dict]) -> bool:
        """Inject patterns via API"""
        return self.client.inject_patterns(patterns)