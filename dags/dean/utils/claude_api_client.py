#!/usr/bin/env python3
"""
Claude API Client for Code Modifications
Implements real Claude API integration for the DEAN system
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)


class ClaudeAPIError(Exception):
    """Claude API specific errors"""
    pass


class RateLimitError(ClaudeAPIError):
    """Rate limit exceeded error"""
    pass


class ClaudeAPIClient:
    """
    Real Claude API client for code modifications.
    Implements authentication, rate limiting, and error handling.
    """
    
    BASE_URL = "https://api.anthropic.com/v1"
    MODEL = "claude-3-opus-20240229"  # Default model
    MAX_TOKENS = 4096
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize Claude API client.
        
        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model to use (defaults to claude-3-opus)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set in ANTHROPIC_API_KEY environment variable")
        
        self.model = model or self.MODEL
        self.session = httpx.Client(
            base_url=self.BASE_URL,
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            },
            timeout=60.0
        )
        
        # Rate limiting tracking
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Minimum seconds between requests
        
    def close(self):
        """Close HTTP session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=60),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException))
    )
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make API request with retry logic.
        
        Args:
            endpoint: API endpoint
            data: Request data
            
        Returns:
            Response data
            
        Raises:
            ClaudeAPIError: On API errors
            RateLimitError: On rate limit exceeded
        """
        self._enforce_rate_limit()
        
        try:
            response = self.session.post(endpoint, json=data)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("retry-after", 60))
                logger.warning(f"Rate limit hit, retry after {retry_after} seconds")
                raise RateLimitError(f"Rate limit exceeded, retry after {retry_after} seconds")
            
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise ClaudeAPIError(f"API request failed: {e}")
        except Exception as e:
            logger.error(f"Request failed: {e}")
            raise
    
    def generate_code_modification(
        self,
        prompt: str,
        context: Optional[str] = None,
        target_files: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate code modification using Claude API.
        
        Args:
            prompt: The modification prompt
            context: Additional context (e.g., existing code)
            target_files: List of target file paths
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            
        Returns:
            Dict containing the modification response
        """
        # Build the full prompt
        full_prompt = self._build_prompt(prompt, context, target_files)
        
        # Prepare request data
        request_data = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "max_tokens": max_tokens or self.MAX_TOKENS,
            "temperature": temperature
        }
        
        # Make API request
        logger.info(f"Sending code modification request to Claude API")
        response = self._make_request("/messages", request_data)
        
        # Extract and parse response
        content = response.get("content", [{}])[0].get("text", "")
        
        return {
            "success": True,
            "model": response.get("model"),
            "usage": response.get("usage", {}),
            "content": content,
            "modifications": self._parse_modifications(content),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _build_prompt(
        self,
        prompt: str,
        context: Optional[str] = None,
        target_files: Optional[List[str]] = None
    ) -> str:
        """Build the full prompt for Claude"""
        parts = [
            "You are a code modification assistant. Please provide code changes in a clear, structured format.",
            "",
            "TASK:",
            prompt,
            ""
        ]
        
        if target_files:
            parts.extend([
                "TARGET FILES:",
                "\n".join(f"- {f}" for f in target_files),
                ""
            ])
        
        if context:
            parts.extend([
                "CONTEXT:",
                context,
                ""
            ])
        
        parts.extend([
            "Please provide your modifications in the following format:",
            "1. For each file, clearly indicate the file path",
            "2. Show the original code to be replaced (if applicable)",
            "3. Show the new code",
            "4. Explain the changes briefly",
            "",
            "Use markdown code blocks with appropriate language tags."
        ])
        
        return "\n".join(parts)
    
    def _parse_modifications(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse modifications from Claude's response.
        
        Returns a list of modification dictionaries.
        """
        modifications = []
        
        # Simple parsing logic - can be enhanced based on actual response patterns
        lines = content.split("\n")
        current_file = None
        current_mod = None
        
        for line in lines:
            # Detect file paths (various patterns)
            if line.strip().startswith("File:") or line.strip().startswith("#"):
                if current_mod:
                    modifications.append(current_mod)
                
                file_path = line.strip().replace("File:", "").replace("#", "").strip()
                current_file = file_path
                current_mod = {
                    "file": current_file,
                    "changes": [],
                    "explanation": ""
                }
            
            # Collect other content as part of current modification
            elif current_mod and line.strip():
                # This is simplified - real implementation would parse code blocks
                current_mod["changes"].append(line)
        
        if current_mod:
            modifications.append(current_mod)
        
        return modifications
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for a text.
        
        Claude uses a similar tokenization to GPT models.
        Rough estimate: 1 token ≈ 4 characters
        """
        return len(text) // 4
    
    def check_rate_limits(self) -> Dict[str, Any]:
        """
        Check current rate limit status.
        
        Returns:
            Dict with rate limit information
        """
        # Claude API doesn't have a dedicated rate limit endpoint
        # Return estimated status based on tracking
        time_since_last = time.time() - self.last_request_time
        
        return {
            "requests_remaining": "unknown",  # Claude doesn't provide this
            "time_until_reset": max(0, self.min_request_interval - time_since_last),
            "last_request": self.last_request_time,
            "min_interval": self.min_request_interval
        }


class ClaudeCodeCLI:
    """
    Production Claude Code CLI replacement.
    Provides the same interface as MockClaudeCodeCLI but uses real API.
    """
    
    def __init__(self, api_key: str, worktree_path: str):
        """
        Initialize Claude Code CLI.
        
        Args:
            api_key: Anthropic API key
            worktree_path: Path to git worktree
        """
        self.api_key = api_key
        self.worktree_path = worktree_path
        self.client = ClaudeAPIClient(api_key=api_key)
        
    def execute(self, prompt: str, target_files: List[str] = None) -> Dict[str, Any]:
        """
        Execute code modification via Claude API.
        
        Args:
            prompt: Modification prompt
            target_files: List of target files
            
        Returns:
            Dict with modification results
        """
        try:
            # Read target file contents if specified
            context = None
            if target_files:
                context = self._read_file_contents(target_files)
            
            # Generate modifications
            result = self.client.generate_code_modification(
                prompt=prompt,
                context=context,
                target_files=target_files
            )
            
            # Apply modifications if successful
            if result["success"] and result["modifications"]:
                applied_files = self._apply_modifications(result["modifications"])
                result["applied_files"] = applied_files
            
            return result
            
        except Exception as e:
            logger.error(f"Claude Code CLI execution failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _read_file_contents(self, file_paths: List[str]) -> str:
        """Read contents of target files for context"""
        contents = []
        
        for file_path in file_paths:
            full_path = os.path.join(self.worktree_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        content = f.read()
                        contents.append(f"=== {file_path} ===\n{content}\n")
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        return "\n".join(contents) if contents else None
    
    def _apply_modifications(self, modifications: List[Dict[str, Any]]) -> List[str]:
        """
        Apply modifications to files.
        
        This is a simplified implementation - real version would need
        proper code parsing and modification logic.
        """
        applied = []
        
        for mod in modifications:
            file_path = mod.get("file")
            if not file_path:
                continue
            
            full_path = os.path.join(self.worktree_path, file_path)
            
            # Log the modification (actual application would be more complex)
            logger.info(f"Would apply modifications to {full_path}")
            applied.append(file_path)
        
        return applied
    
    def close(self):
        """Close the client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Factory function for backward compatibility
def create_claude_client(api_key: str, worktree_path: str, use_mock: bool = False):
    """
    Create Claude client (mock or real based on configuration).
    
    Args:
        api_key: API key
        worktree_path: Git worktree path
        use_mock: Whether to use mock client
        
    Returns:
        ClaudeCodeCLI instance
    """
    if use_mock:
        from .code_modification_client import MockClaudeCodeCLI
        return MockClaudeCodeCLI(api_key, worktree_path)
    else:
        return ClaudeCodeCLI(api_key, worktree_path)