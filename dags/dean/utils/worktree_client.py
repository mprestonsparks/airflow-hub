#!/usr/bin/env python3
"""
Git Worktree Management API Client
"""

import os
import logging
from typing import Dict, Any, Optional
import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


class WorktreeClient:
    """Client for managing git worktrees via API"""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = Variable.get("dean_api_url", os.environ.get("DEAN_API_URL", "http://infra-api:8091"))
        
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def create_worktree(self, agent_id: str, base_repo: str = "/repos/target") -> str:
        """Create isolated worktree for agent"""
        try:
            payload = {"agent_id": agent_id, "base_repo": base_repo}
            response = self.session.post(f"{self.base_url}/api/v1/worktrees", json=payload)
            response.raise_for_status()
            return response.json()["worktree_path"]
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create worktree for {agent_id}: {e}")
            raise
    
    def get_worktree_info(self, agent_id: str) -> Dict[str, Any]:
        """Get worktree information"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/worktrees/{agent_id}")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get worktree info for {agent_id}: {e}")
            raise
    
    def cleanup_worktree(self, agent_id: str) -> bool:
        """Remove worktree after use"""
        try:
            response = self.session.delete(f"{self.base_url}/api/v1/worktrees/{agent_id}")
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to cleanup worktree for {agent_id}: {e}")
            return False
    
    def close(self):
        """Close HTTP session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()