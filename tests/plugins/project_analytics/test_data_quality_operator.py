"""
Tests for the DataQualityOperator.

This module contains unit tests for the DataQualityOperator to ensure
it correctly performs data quality checks.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from plugins.project_analytics.operators.data_quality_operator import DataQualityOperator


class TestDataQualityOperator:
    """Test suite for DataQualityOperator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.conn_id = 'project_analytics_snowflake_test'
        self.table = 'test_table'
        self.checks = [
            {'type': 'not_null', 'columns': ['id', 'value']},
            {'type': 'unique', 'columns': ['id']},
            {'type': 'value_range', 'column': 'value', 'min': 0, 'max': 100},
            {'type': 'row_count', 'min_rows': 1, 'max_rows': 1000}
        ]
        
        # Create operator instance
        self.operator = DataQualityOperator(
            task_id='test_data_quality',
            conn_id=self.conn_id,
            table=self.table,
            checks=self.checks
        )
        
        # Mock Airflow context
        self.context = {}
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_init(self, mock_db_hook):
        """Test operator initialization."""
        # Assert operator attributes
        assert self.operator.conn_id == self.conn_id
        assert self.operator.table == self.table
        assert self.operator.checks == self.checks
        assert self.operator.fail_on_error is True
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_all_checks_pass(self, mock_db_hook_class):
        """Test execute method when all checks pass."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create test data that will pass all checks
        test_data = [
            {'id': 1, 'value': 50},
            {'id': 2, 'value': 75}
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator
        result = self.operator.execute(self.context)
        
        # Verify the result
        assert result['passed'] is True
        assert len(result['checks']) == len(self.checks)
        for check_result in result['checks']:
            assert check_result['passed'] is True
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_null_check_fails(self, mock_db_hook_class):
        """Test execute method when null check fails."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create test data with null values
        test_data = [
            {'id': 1, 'value': None},
            {'id': 2, 'value': 75}
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator with fail_on_error=False to prevent exception
        self.operator.fail_on_error = False
        result = self.operator.execute(self.context)
        
        # Verify the result
        assert result['passed'] is False
        assert any(not check['passed'] for check in result['checks'])
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_unique_check_fails(self, mock_db_hook_class):
        """Test execute method when unique check fails."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create test data with duplicate IDs
        test_data = [
            {'id': 1, 'value': 50},
            {'id': 1, 'value': 75}  # Duplicate ID
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator with fail_on_error=False to prevent exception
        self.operator.fail_on_error = False
        result = self.operator.execute(self.context)
        
        # Verify the result
        assert result['passed'] is False
        assert any(not check['passed'] for check in result['checks'])
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_value_range_check_fails(self, mock_db_hook_class):
        """Test execute method when value range check fails."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create test data with out-of-range value
        test_data = [
            {'id': 1, 'value': 50},
            {'id': 2, 'value': 150}  # Value > max (100)
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator with fail_on_error=False to prevent exception
        self.operator.fail_on_error = False
        result = self.operator.execute(self.context)
        
        # Verify the result
        assert result['passed'] is False
        assert any(not check['passed'] for check in result['checks'])
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_row_count_check_fails(self, mock_db_hook_class):
        """Test execute method when row count check fails."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create empty test data (fails min_rows=1)
        test_data = []
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator with fail_on_error=False to prevent exception
        self.operator.fail_on_error = False
        result = self.operator.execute(self.context)
        
        # Verify the result
        assert result['passed'] is False
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_with_custom_sql(self, mock_db_hook_class):
        """Test execute method with custom SQL query."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Set custom SQL query
        custom_sql = "SELECT * FROM test_table WHERE value > 0"
        self.operator.sql_query = custom_sql
        
        # Create test data
        test_data = [
            {'id': 1, 'value': 50},
            {'id': 2, 'value': 75}
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator
        self.operator.execute(self.context)
        
        # Verify the SQL query was used
        mock_db_hook.run_query.assert_called_once_with(custom_sql)
    
    @patch('plugins.common.hooks.database_hook.DatabaseHook')
    def test_execute_fail_on_error(self, mock_db_hook_class):
        """Test execute method raises exception when checks fail and fail_on_error=True."""
        # Setup mock
        mock_db_hook = MagicMock()
        mock_db_hook_class.return_value = mock_db_hook
        
        # Create test data with null values
        test_data = [
            {'id': 1, 'value': None},
            {'id': 2, 'value': 75}
        ]
        mock_db_hook.run_query.return_value = test_data
        
        # Execute the operator with fail_on_error=True
        self.operator.fail_on_error = True
        
        # Expect ValueError to be raised
        with pytest.raises(ValueError):
            self.operator.execute(self.context)
