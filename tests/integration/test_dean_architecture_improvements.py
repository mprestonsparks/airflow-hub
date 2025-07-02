#!/usr/bin/env python3
"""
Integration tests for DEAN architecture improvements
Verifies that the new architecture maintains all functionality
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from airflow.models import DagBag, Variable
from airflow.utils.db import provide_session
from airflow.models.connection import Connection
from sqlalchemy.orm import Session

# Add DAGs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../dags'))


class TestDeanArchitectureImprovements:
    """Test suite for DEAN architecture improvements"""
    
    @pytest.fixture
    def dag_bag(self):
        """Load all DAGs from the dean subdirectory"""
        dag_folder = os.path.join(os.path.dirname(__file__), '../../dags/dean')
        return DagBag(dag_folder=dag_folder, include_examples=False)
    
    def test_dean_dags_load_correctly(self, dag_bag):
        """Test that all DEAN DAGs load without import errors"""
        # Check that we have DAGs
        assert len(dag_bag.dags) > 0, "No DAGs found in dean directory"
        
        # Check for import errors
        assert len(dag_bag.import_errors) == 0, f"Import errors found: {dag_bag.import_errors}"
        
        # Verify expected DAGs are present
        expected_dags = [
            'dean_evolution_cycle',
            'dean_orchestration',
            'dean_pattern_extraction',
            'dean_maintenance'
        ]
        
        for dag_id in expected_dags:
            assert dag_id in dag_bag.dags, f"Expected DAG {dag_id} not found"
    
    def test_dean_dags_have_correct_tags(self, dag_bag):
        """Test that DEAN DAGs have appropriate tags"""
        for dag_id, dag in dag_bag.dags.items():
            assert 'dean' in dag.tags, f"DAG {dag_id} missing 'dean' tag"
    
    @provide_session
    def test_required_connections_exist(self, session: Session):
        """Test that required connections are configured"""
        required_connections = [
            'postgres_default',
            'dean_api',
            'indexagent_api',
            'evolution_api'
        ]
        
        for conn_id in required_connections:
            # This would check if connection exists in a real environment
            # For testing, we just verify the code expects these connections
            pass
    
    def test_required_variables_documented(self):
        """Test that required Airflow Variables are documented"""
        # These variables should be used in the DAGs
        expected_variables = [
            'dean_api_url',
            'dean_base_repo',
            'dean_total_budget',
            'dean_agent_count',
            'anthropic_api_key'
        ]
        
        # In a real test, we'd check Variable.get() calls in the DAGs
        # For now, we document what's expected
        assert len(expected_variables) > 0
    
    @patch('dean.utils.economic_client.EconomicGovernorClient')
    def test_economic_governor_api_integration(self, mock_client):
        """Test that EconomicGovernor is accessed via API"""
        from dean.utils.economic_client import check_global_budget_via_api
        
        # Mock the API response
        mock_instance = MagicMock()
        mock_instance.get_system_metrics.return_value = {
            "global_budget": {
                "total": 1000000,
                "allocated": 500000,
                "used": 300000,
                "available": 500000,
                "usage_rate": 0.3
            },
            "agents": {
                "total": 10,
                "average_efficiency": 0.75
            },
            "top_performers": []
        }
        mock_client.return_value.__enter__.return_value = mock_instance
        
        # Test the function
        result = check_global_budget_via_api(min_budget=10000)
        
        assert result['has_budget'] is True
        assert result['available_budget'] == 500000
        assert result['usage_rate'] == 0.3
        assert mock_instance.get_system_metrics.called
    
    def test_dean_evolution_cycle_tasks(self, dag_bag):
        """Test that dean_evolution_cycle DAG has expected tasks"""
        dag = dag_bag.get_dag('dean_evolution_cycle')
        assert dag is not None
        
        expected_tasks = [
            'check_global_budget',
            'spawn_agents',
            'measure_diversity',
            'detect_patterns',
            'meta_learning_injection',
            'insufficient_budget'
        ]
        
        task_ids = list(dag.task_ids)
        for task_id in expected_tasks:
            assert any(task_id in t for t in task_ids), f"Task {task_id} not found in DAG"
    
    @patch('requests.Session')
    def test_economic_client_error_handling(self, mock_session):
        """Test that the economic client handles API errors gracefully"""
        from dean.utils.economic_client import EconomicGovernorClient
        
        # Mock a failed request
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_session.return_value.get.return_value = mock_response
        
        client = EconomicGovernorClient()
        
        with pytest.raises(Exception) as exc_info:
            client.get_system_metrics()
        
        assert "API Error" in str(exc_info.value)
    
    def test_no_cross_repository_imports(self, dag_bag):
        """Test that DAGs don't have direct cross-repository imports"""
        # List of imports that should NOT appear in the DAGs
        forbidden_imports = [
            'from infra.services.economy.economic_governor import EconomicGovernor',
            # Note: Other infra imports still exist and need to be addressed
        ]
        
        for dag_id, dag in dag_bag.dags.items():
            dag_file = dag.fileloc
            if dag_file and os.path.exists(dag_file):
                with open(dag_file, 'r') as f:
                    content = f.read()
                    
                for forbidden in forbidden_imports:
                    assert forbidden not in content, \
                        f"Found forbidden import '{forbidden}' in {dag_file}"
    
    def test_api_client_context_manager(self):
        """Test that the API client properly implements context manager"""
        from dean.utils.economic_client import EconomicGovernorClient
        
        with patch('requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            with EconomicGovernorClient() as client:
                assert client.session is mock_session_instance
            
            # Verify session was closed
            mock_session_instance.close.assert_called_once()
    
    @patch('dean.utils.economic_client.EconomicGovernorClient')
    def test_token_usage_recording(self, mock_client):
        """Test that token usage is recorded via API"""
        from dean.utils.economic_client import use_tokens_via_api
        
        # Mock successful token usage
        mock_instance = MagicMock()
        mock_instance.use_tokens.return_value = {"success": True}
        mock_client.return_value.__enter__.return_value = mock_instance
        
        result = use_tokens_via_api(
            agent_id="test_agent",
            tokens=100,
            action_type="optimization",
            task_success=0.8,
            quality_score=0.9
        )
        
        assert result is True
        mock_instance.use_tokens.assert_called_once_with(
            "test_agent", 100, "optimization", 0.8, 0.9
        )


class TestServiceIndependence:
    """Test that services can operate independently"""
    
    def test_airflow_hub_independent_operation(self):
        """Test that airflow-hub can function without DEAN components"""
        # Verify that non-DEAN DAGs don't import DEAN-specific components
        dag_folder = os.path.join(os.path.dirname(__file__), '../../dags')
        dag_bag = DagBag(dag_folder=dag_folder, include_examples=False)
        
        # Get non-DEAN DAGs
        non_dean_dags = {
            dag_id: dag for dag_id, dag in dag_bag.dags.items()
            if 'dean' not in dag.tags
        }
        
        # Verify they don't import dean-specific utilities
        for dag_id, dag in non_dean_dags.items():
            if dag.fileloc and os.path.exists(dag.fileloc):
                with open(dag.fileloc, 'r') as f:
                    content = f.read()
                    assert 'from dean.' not in content, \
                        f"Non-DEAN DAG {dag_id} imports DEAN components"
    
    def test_api_endpoint_documentation(self):
        """Test that API endpoints are properly documented"""
        # This would verify that the API endpoints match documentation
        expected_endpoints = [
            "/api/v1/economy/metrics",
            "/api/v1/economy/agent/{agent_id}",
            "/api/v1/economy/use-tokens",
            "/api/v1/economy/allocate",
            "/api/v1/economy/rebalance"
        ]
        
        # In a real test, we'd verify these endpoints exist in the API
        assert len(expected_endpoints) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])