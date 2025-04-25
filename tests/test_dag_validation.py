"""
DAG validation tests.

This module contains tests to validate that all DAGs are correctly defined
and can be loaded without errors.
"""

import pytest
from airflow.models import DagBag

def test_dag_loading():
    """Test that all DAGs can be loaded without import errors."""
    dag_bag = DagBag(dag_folder="../dags", include_examples=False)
    assert not dag_bag.import_errors, f"DAG import errors: {dag_bag.import_errors}"
    assert len(dag_bag.dag_ids) > 0, f"No DAGs found in {dag_bag.dag_folder}"

def test_dag_default_args():
    """Test that all DAGs have required default arguments."""
    dag_bag = DagBag(dag_folder="../dags", include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Skip system test DAGs
        if dag_id.startswith('test_'):
            continue
        
        # Check for required default args
        assert hasattr(dag, 'default_args'), f"DAG {dag_id} has no default_args"
        assert 'owner' in dag.default_args, f"DAG {dag_id} has no owner in default_args"
        assert 'retries' in dag.default_args, f"DAG {dag_id} has no retries in default_args"


def test_dag_tags():
    """Test that all DAGs have tags."""
    dag_bag = DagBag(dag_folder="../dags", include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Skip system test DAGs
        if dag_id.startswith('test_'):
            continue
        
        assert hasattr(dag, 'tags'), f"DAG {dag_id} has no tags"
        assert len(dag.tags) > 0, f"DAG {dag_id} has empty tags"
