#!/usr/bin/env python3
"""
Code Modification Service API Client
"""

import os
import logging
import time
from typing import Dict, Any, Optional, List
import requests
from airflow.models import Variable

logger = logging.getLogger(__name__)


class CodeModificationClient:
    """Client for code modifications via API"""
    
    def __init__(self, base_url: Optional[str] = None):
        if base_url is None:
            base_url = Variable.get("dean_api_url", os.environ.get("DEAN_API_URL", "http://infra-api:8091"))
        
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.api_key = Variable.get("anthropic_api_key", os.environ.get("ANTHROPIC_API_KEY", "mock_key"))
    
    def execute_modification(self, agent_id: str, worktree_path: str, 
                           prompt: str, target_files: List[str] = None,
                           max_tokens: int = 4096) -> Dict[str, Any]:
        """Execute code modification and wait for result"""
        try:
            # Submit modification request
            payload = {
                "agent_id": agent_id,
                "worktree_path": worktree_path,
                "prompt": prompt,
                "target_files": target_files or [],
                "max_tokens": max_tokens
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/modifications",
                json=payload,
                headers={"X-API-Key": self.api_key}
            )
            response.raise_for_status()
            task_id = response.json()["task_id"]
            
            # Poll for result
            max_attempts = 60  # 5 minute timeout
            for attempt in range(max_attempts):
                result_response = self.session.get(
                    f"{self.base_url}/api/v1/modifications/{task_id}"
                )
                
                if result_response.status_code == 200:
                    result = result_response.json()
                    if result["status"] == "completed":
                        return result
                    elif result["status"] == "failed":
                        raise Exception(f"Modification failed: {result.get('error')}")
                
                time.sleep(5)  # Wait 5 seconds before retry
            
            raise TimeoutError("Modification timed out after 5 minutes")
            
        except Exception as e:
            logger.error(f"Failed to execute modification: {e}")
            raise
    
    def close(self):
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class MockClaudeCodeCLI:
    """Mock wrapper for backward compatibility"""
    
    def __init__(self, api_key: str, worktree_path: str):
        self.api_key = api_key
        self.worktree_path = worktree_path
        self.client = CodeModificationClient()
    
    def execute(self, prompt: str, target_files: List[str] = None) -> Dict[str, Any]:
        """Execute modification via API"""
        agent_id = os.path.basename(self.worktree_path)  # Extract agent ID from path
        return self.client.execute_modification(
            agent_id=agent_id,
            worktree_path=self.worktree_path,
            prompt=prompt,
            target_files=target_files
        )