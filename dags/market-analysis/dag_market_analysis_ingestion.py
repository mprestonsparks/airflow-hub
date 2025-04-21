"""
Market Analysis Ingestion DAG.

This DAG uses the `market-analysis:latest` Docker image to fetch daily market data
for a specified symbol and date using the market-analysis script.
"""
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Default arguments for the DAG
DEFAULT_ARGS = {
    'owner': 'analytics_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'pool': 'project_market_analysis_pool',
}

# Define the DAG
dag = DAG(
    'market_analysis_ingestion',
    default_args=DEFAULT_ARGS,
    description='Ingest market data via market-analysis container',
    schedule_interval='@daily',
    start_date=days_ago(1),
    tags=['market-analysis', 'ingestion'],
)
# Use module docstring in Airflow UI
dag.doc_md = __doc__

# Task: Run the ingestion script in the Docker container
ingest_task = DockerOperator(
    task_id='ingest_market_data',
    image='market-analysis:latest',
    command=[
        'python', '-m', 'src.main',
        '--symbol', '{{ params.symbol }}',
        '--start', '{{ ds }}',
        '--end', '{{ ds }}',
    ],
    params={'symbol': 'AAPL'},
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    dag=dag,
)