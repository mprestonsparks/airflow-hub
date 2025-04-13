"""
Tests for the analytics_daily_etl DAG.

This module contains tests to validate the structure and functionality
of the analytics daily ETL DAG.
"""

import pytest
from airflow.models import DagBag
from airflow.utils.session import create_session
from airflow.utils.state import State


class TestAnalyticsDailyEtlDag:
    """Test suite for analytics_daily_etl DAG."""
    
    @pytest.fixture
    def dagbag(self):
        """Create a DagBag fixture."""
        return DagBag(include_examples=False)
    
    def test_dag_loaded(self, dagbag):
        """Test that the DAG is loaded correctly."""
        dag_id = 'project_analytics_daily_etl'
        assert dag_id in dagbag.dag_ids
        assert dagbag.import_errors == {}
    
    def test_dag_structure(self, dagbag):
        """Test the structure of the DAG."""
        dag_id = 'project_analytics_daily_etl'
        dag = dagbag.get_dag(dag_id)
        
        # Check basic DAG properties
        assert 'analytics' in dag.tags
        assert 'etl' in dag.tags
        assert 'ml' in dag.tags
        assert dag.description == 'Daily ETL process for analytics data'
        
        # Check default args
        assert dag.default_args['owner'] == 'analytics_team'
        assert dag.default_args['retries'] == 2
        assert dag.default_args['pool'] == 'project_analytics_pool'
        
        # Check tasks
        tasks = dag.tasks
        task_ids = [task.task_id for task in tasks]
        
        assert 'extract_transform_data' in task_ids
        assert 'check_data_quality' in task_ids
        assert 'run_ml_predictions' in task_ids
        assert 'generate_reports' in task_ids
        
        # Check task types
        extract_transform_task = next(task for task in tasks if task.task_id == 'extract_transform_data')
        data_quality_task = next(task for task in tasks if task.task_id == 'check_data_quality')
        ml_prediction_task = next(task for task in tasks if task.task_id == 'run_ml_predictions')
        generate_reports_task = next(task for task in tasks if task.task_id == 'generate_reports')
        
        from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
        from plugins.project_analytics.operators import DataQualityOperator, MLPredictionOperator
        
        assert isinstance(extract_transform_task, SnowflakeOperator)
        assert isinstance(data_quality_task, DataQualityOperator)
        assert isinstance(ml_prediction_task, MLPredictionOperator)
        assert isinstance(generate_reports_task, SnowflakeOperator)
    
    def test_task_dependencies(self, dagbag):
        """Test the task dependencies in the DAG."""
        dag_id = 'project_analytics_daily_etl'
        dag = dagbag.get_dag(dag_id)
        
        # Get tasks
        extract_transform_task = dag.get_task('extract_transform_data')
        data_quality_task = dag.get_task('check_data_quality')
        ml_prediction_task = dag.get_task('run_ml_predictions')
        generate_reports_task = dag.get_task('generate_reports')
        
        # Check dependencies
        assert extract_transform_task.downstream_task_ids == {'check_data_quality'}
        assert data_quality_task.downstream_task_ids == {'run_ml_predictions'}
        assert ml_prediction_task.downstream_task_ids == {'generate_reports'}
        assert generate_reports_task.downstream_task_ids == set()
        
        # Check upstream dependencies
        assert extract_transform_task.upstream_task_ids == set()
        assert data_quality_task.upstream_task_ids == {'extract_transform_data'}
        assert ml_prediction_task.upstream_task_ids == {'check_data_quality'}
        assert generate_reports_task.upstream_task_ids == {'run_ml_predictions'}
    
    def test_task_configuration(self, dagbag):
        """Test the configuration of individual tasks."""
        dag_id = 'project_analytics_daily_etl'
        dag = dagbag.get_dag(dag_id)
        
        # Check extract_transform task configuration
        extract_transform_task = dag.get_task('extract_transform_data')
        assert extract_transform_task.snowflake_conn_id == 'project_analytics_snowflake'
        assert "CALL analytics.etl_process_daily" in extract_transform_task.sql
        
        # Check data_quality task configuration
        data_quality_task = dag.get_task('check_data_quality')
        assert data_quality_task.conn_id == 'project_analytics_snowflake'
        assert data_quality_task.table == 'analytics.processed_data'
        assert len(data_quality_task.checks) == 4
        
        # Check ml_prediction task configuration
        ml_prediction_task = dag.get_task('run_ml_predictions')
        assert ml_prediction_task.conn_id == 'project_analytics_snowflake'
        assert ml_prediction_task.model_path == '/opt/airflow/ml_models/customer_churn_model.pkl'
        assert ml_prediction_task.output_table == 'analytics.churn_predictions'
        assert len(ml_prediction_task.features) == 5
        
        # Check generate_reports task configuration
        generate_reports_task = dag.get_task('generate_reports')
        assert generate_reports_task.snowflake_conn_id == 'project_analytics_snowflake'
        assert "CALL analytics.generate_daily_reports" in generate_reports_task.sql
