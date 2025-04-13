"""
DAG validation tests.

This module contains tests to validate that all DAGs are correctly defined
and can be loaded without errors.
"""

import pytest
from airflow.models import DagBag
import os


def test_dag_loading():
    """Test that all DAGs can be loaded without import errors."""
    dag_bag = DagBag(include_examples=False)
    
    # Check for import errors
    assert not dag_bag.import_errors, f"DAG import errors: {dag_bag.import_errors}"
    
    # Check that we have DAGs
    assert len(dag_bag.dag_ids) > 0, "No DAGs found"


def test_project_dag_structure():
    """Test that project DAGs follow naming conventions and structure."""
    dag_bag = DagBag(include_examples=False)
    
    # Get all DAGs by project
    projects = {}
    for dag_id in dag_bag.dag_ids:
        if dag_id.startswith('project_'):
            # Extract project name (e.g., 'project_trading' from 'project_trading_daily_sync')
            parts = dag_id.split('_')
            if len(parts) >= 2:
                project = f"{parts[0]}_{parts[1]}"
                if project not in projects:
                    projects[project] = []
                projects[project].append(dag_id)
    
    # Check that each project has at least one DAG
    for project, dag_ids in projects.items():
        assert len(dag_ids) > 0, f"Project {project} has no DAGs"


def test_dag_default_args():
    """Test that all DAGs have required default arguments."""
    dag_bag = DagBag(include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Skip system test DAGs
        if dag_id.startswith('test_'):
            continue
        
        # Check for required default args
        assert hasattr(dag, 'default_args'), f"DAG {dag_id} has no default_args"
        assert 'owner' in dag.default_args, f"DAG {dag_id} has no owner in default_args"
        assert 'retries' in dag.default_args, f"DAG {dag_id} has no retries in default_args"


def test_project_specific_pools():
    """Test that project DAGs use project-specific pools."""
    dag_bag = DagBag(include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Only check project DAGs
        if not dag_id.startswith('project_'):
            continue
        
        # Extract project name
        parts = dag_id.split('_')
        if len(parts) >= 2:
            project = f"{parts[0]}_{parts[1]}"
            
            # Check if pool is specified in default args
            if 'pool' in dag.default_args:
                pool = dag.default_args['pool']
                assert pool.startswith(project), f"DAG {dag_id} uses non-project pool: {pool}"


def test_dag_tags():
    """Test that all DAGs have tags."""
    dag_bag = DagBag(include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Skip system test DAGs
        if dag_id.startswith('test_'):
            continue
        
        assert hasattr(dag, 'tags'), f"DAG {dag_id} has no tags"
        assert len(dag.tags) > 0, f"DAG {dag_id} has empty tags"


def test_dag_documentation():
    """Test that all DAGs have docstrings."""
    dag_bag = DagBag(include_examples=False)
    
    for dag_id, dag in dag_bag.dags.items():
        # Skip system test DAGs
        if dag_id.startswith('test_'):
            continue
        
        assert dag.doc_md is not None, f"DAG {dag_id} has no documentation"
        assert len(dag.doc_md) > 0, f"DAG {dag_id} has empty documentation"
