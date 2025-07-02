#!/usr/bin/env python3
"""
Tests for Economic Governor API Client
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, Mock
import requests

# Add DAGs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../dags'))

from dean.utils.economic_client import EconomicGovernorClient, check_global_budget_via_api, use_tokens_via_api


class TestEconomicGovernorClient:
    """Test Economic Governor API client"""
    
    @pytest.fixture
    def client(self):
        """Create client instance"""
        with patch('dean.utils.economic_client.Variable') as mock_var:
            mock_var.get.return_value = "http://test-api:8091"
            return EconomicGovernorClient()
    
    def test_client_initialization(self):
        """Test client initializes with correct base URL"""
        with patch('dean.utils.economic_client.Variable') as mock_var:
            mock_var.get.return_value = "http://custom-api:9000"
            client = EconomicGovernorClient()
            assert client.base_url == "http://custom-api:9000"
    
    def test_get_system_metrics_success(self, client):
        """Test successful system metrics retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "global_budget": {
                "total": 1000000,
                "available": 500000,
                "usage_rate": 0.5
            }
        }
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            result = client.get_system_metrics()
            
            mock_get.assert_called_once_with("http://test-api:8091/api/v1/economy/metrics")
            assert result["global_budget"]["total"] == 1000000
    
    def test_get_system_metrics_failure(self, client):
        """Test system metrics retrieval with API error"""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server error")
        
        with patch.object(client.session, 'get', return_value=mock_response):
            with pytest.raises(requests.exceptions.HTTPError):
                client.get_system_metrics()
    
    def test_use_tokens_success(self, client):
        """Test successful token usage recording"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "success": True,
            "remaining_budget": 900
        }
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            result = client.use_tokens(
                agent_id="test_agent",
                tokens=100,
                action_type="optimization",
                task_success=0.8,
                quality_score=0.9
            )
            
            mock_post.assert_called_once()
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://test-api:8091/api/v1/economy/use-tokens"
            assert call_args[1]['json']['agent_id'] == "test_agent"
            assert call_args[1]['json']['tokens'] == 100
            assert result["success"] is True
    
    def test_check_budget_allows_action(self, client):
        """Test budget checking for actions"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "budget": {"remaining": 500}
        }
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = client.check_budget_allows_action("test_agent", 100)
            assert result is True
            
            result = client.check_budget_allows_action("test_agent", 600)
            assert result is False
    
    def test_context_manager(self):
        """Test client works as context manager"""
        with patch('dean.utils.economic_client.Variable') as mock_var:
            mock_var.get.return_value = "http://test-api:8091"
            
            with EconomicGovernorClient() as client:
                assert client.session is not None
                mock_close = Mock()
                client.session.close = mock_close
            
            mock_close.assert_called_once()
    
    def test_convenience_function_check_global_budget(self):
        """Test check_global_budget_via_api convenience function"""
        with patch('dean.utils.economic_client.EconomicGovernorClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.get_system_metrics.return_value = {
                "global_budget": {
                    "available": 50000,
                    "usage_rate": 0.5
                }
            }
            mock_client_class.return_value.__enter__.return_value = mock_instance
            
            result = check_global_budget_via_api(min_budget=10000)
            
            assert result["has_budget"] is True
            assert result["available_budget"] == 50000
            assert result["usage_rate"] == 0.5
    
    def test_convenience_function_use_tokens(self):
        """Test use_tokens_via_api convenience function"""
        with patch('dean.utils.economic_client.EconomicGovernorClient') as mock_client_class:
            mock_instance = MagicMock()
            mock_instance.use_tokens.return_value = {"success": True}
            mock_client_class.return_value.__enter__.return_value = mock_instance
            
            result = use_tokens_via_api(
                agent_id="test_agent",
                tokens=100,
                action_type="test",
                task_success=1.0,
                quality_score=1.0
            )
            
            assert result is True
            
            # Test failure case
            mock_instance.use_tokens.side_effect = Exception("API Error")
            result = use_tokens_via_api("test_agent", 100, "test", 1.0, 1.0)
            assert result is False


class TestAllAPIClients:
    """Test all API clients are properly implemented"""
    
    def test_worktree_client_exists(self):
        """Test WorktreeClient is implemented"""
        from dean.utils.worktree_client import WorktreeClient
        assert WorktreeClient is not None
    
    def test_code_modification_client_exists(self):
        """Test CodeModificationClient is implemented"""
        from dean.utils.code_modification_client import CodeModificationClient, MockClaudeCodeCLI
        assert CodeModificationClient is not None
        assert MockClaudeCodeCLI is not None
    
    def test_optimization_client_exists(self):
        """Test OptimizationClient is implemented"""
        from dean.utils.optimization_client import OptimizationClient, DEANOptimizer
        assert OptimizationClient is not None
        assert DEANOptimizer is not None
    
    def test_diversity_client_exists(self):
        """Test DiversityClient is implemented"""
        from dean.utils.diversity_client import DiversityClient, DiversityManager
        assert DiversityClient is not None
        assert DiversityManager is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])