"""
Tests for the market_analysis_ingestion DAG in airflow-hub.
"""

import pytest
from airflow.models import DagBag
from airflow.providers.docker.operators.docker import DockerOperator


@pytest.fixture(scope='session')
def dag_bag():
    return DagBag(include_examples=False)


def test_market_analysis_dag_loaded(dag_bag):
    assert 'market_analysis_ingestion' in dag_bag.dag_ids, \
        "market_analysis_ingestion DAG should be present"
    dag = dag_bag.get_dag('market_analysis_ingestion')
    assert dag is not None
    assert dag.doc_md is not None and len(dag.doc_md) > 0, \
        "market_analysis_ingestion DAG should have documentation"


def test_market_analysis_docker_operator(dag_bag):
    dag = dag_bag.get_dag('market_analysis_ingestion')
    task = dag.get_task('ingest_market_data')
    assert isinstance(task, DockerOperator), \
        "ingest_market_data should be a DockerOperator"
    assert task.image == 'market-analysis:latest'
    # Ensure command uses the correct entrypoint
    cmd = task.command
    assert 'python' in cmd[0]
    assert '--symbol' in cmd
    # Check default_args pool
    assert dag.default_args.get('pool') == 'project_market_analysis_pool'