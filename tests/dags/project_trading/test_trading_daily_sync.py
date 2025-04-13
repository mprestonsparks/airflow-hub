"""
Tests for the trading_daily_sync DAG.

This module contains tests to validate the structure and functionality
of the trading daily synchronization DAG.
"""

import pytest
from airflow.models import DagBag
from airflow.utils.session import create_session
from airflow.utils.state import State


class TestTradingDailySyncDag:
    """Test suite for trading_daily_sync DAG."""
    
    @pytest.fixture
    def dagbag(self):
        """Create a DagBag fixture."""
        return DagBag(include_examples=False)
    
    def test_dag_loaded(self, dagbag):
        """Test that the DAG is loaded correctly."""
        dag_id = 'project_trading_daily_sync'
        assert dag_id in dagbag.dag_ids
        assert dagbag.import_errors == {}
    
    def test_dag_structure(self, dagbag):
        """Test the structure of the DAG."""
        dag_id = 'project_trading_daily_sync'
        dag = dagbag.get_dag(dag_id)
        
        # Check basic DAG properties
        assert dag.tags == ['trading', 'ibkr']
        assert dag.description == 'Syncs daily trading data from IBKR to data warehouse'
        
        # Check default args
        assert dag.default_args['owner'] == 'trading_team'
        assert dag.default_args['retries'] == 3
        assert dag.default_args['pool'] == 'project_trading_pool'
        
        # Check tasks
        tasks = dag.tasks
        task_ids = [task.task_id for task in tasks]
        
        assert 'extract_ibkr_data' in task_ids
        assert 'process_trading_data' in task_ids
        assert 'load_processed_data' in task_ids
        
        # Check task types
        extract_task = next(task for task in tasks if task.task_id == 'extract_ibkr_data')
        process_task = next(task for task in tasks if task.task_id == 'process_trading_data')
        load_task = next(task for task in tasks if task.task_id == 'load_processed_data')
        
        from plugins.project_trading.operators import IBKRDataOperator
        from airflow.providers.docker.operators.docker import DockerOperator
        from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
        
        assert isinstance(extract_task, IBKRDataOperator)
        assert isinstance(process_task, DockerOperator)
        assert isinstance(load_task, SnowflakeOperator)
    
    def test_task_dependencies(self, dagbag):
        """Test the task dependencies in the DAG."""
        dag_id = 'project_trading_daily_sync'
        dag = dagbag.get_dag(dag_id)
        
        # Get tasks
        extract_task = dag.get_task('extract_ibkr_data')
        process_task = dag.get_task('process_trading_data')
        load_task = dag.get_task('load_processed_data')
        
        # Check dependencies
        assert extract_task.downstream_task_ids == {'process_trading_data'}
        assert process_task.downstream_task_ids == {'load_processed_data'}
        assert load_task.downstream_task_ids == set()
        
        # Check upstream dependencies
        assert extract_task.upstream_task_ids == set()
        assert process_task.upstream_task_ids == {'extract_ibkr_data'}
        assert load_task.upstream_task_ids == {'process_trading_data'}
    
    def test_task_configuration(self, dagbag):
        """Test the configuration of individual tasks."""
        dag_id = 'project_trading_daily_sync'
        dag = dagbag.get_dag(dag_id)
        
        # Check extract task configuration
        extract_task = dag.get_task('extract_ibkr_data')
        assert extract_task.conn_id == 'project_trading_ibkr'
        assert extract_task.data_types == ['trades', 'positions', 'market_data']
        assert extract_task.output_path == '/tmp/data/{{ ds }}'
        
        # Check process task configuration
        process_task = dag.get_task('process_trading_data')
        assert process_task.image == 'trading-project:latest'
        assert 'DATA_DATE' in process_task.environment
        assert 'DATA_PATH' in process_task.environment
        
        # Check load task configuration
        load_task = dag.get_task('load_processed_data')
        assert load_task.snowflake_conn_id == 'project_trading_snowflake'
        assert "CALL trading.load_daily_data" in load_task.sql
