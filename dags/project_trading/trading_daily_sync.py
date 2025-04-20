"""
Daily trading data synchronization DAG.

This DAG extracts trading data from Interactive Brokers, processes it,
and loads it into a data warehouse for analysis.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from plugins.project_trading.operators import IBKRDataOperator

# Configuration with project-specific naming conventions
DEFAULT_ARGS = {
    'owner': 'trading_team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': 300,  # 5 minutes
    'pool': 'project_trading_pool',  # Project-specific resource pool
}

# DAG ID has project prefix for clear identification
dag = DAG(
    'project_trading_daily_sync',
    default_args=DEFAULT_ARGS,
    description='Syncs daily trading data from IBKR to data warehouse',
    schedule_interval='0 1 * * *',  # 1:00 AM daily
    start_date=days_ago(1),
    tags=['trading', 'ibkr'],
)
# Use module docstring as DAG documentation
dag.doc_md = __doc__

# Extract task using project-specific operator
extract_task = IBKRDataOperator(
    task_id='extract_ibkr_data',
    conn_id='project_trading_ibkr',  # Project-specific connection
    data_types=['trades', 'positions', 'market_data'],
    output_path='/tmp/data/{{ ds }}',
    dag=dag,
)

# Processing task using containerized execution for dependency isolation
process_task = DockerOperator(
    task_id='process_trading_data',
    image='trading-project:latest',
    command='python /scripts/process_trading_data.py',
    environment={
        'DATA_DATE': '{{ ds }}',
        'DATA_PATH': '/tmp/data/{{ ds }}',
    },
    docker_url='unix://var/run/docker.sock',
    network_mode='bridge',
    dag=dag,
)

# Data load task with project-specific connection
load_task = SnowflakeOperator(
    task_id='load_processed_data',
    snowflake_conn_id='project_trading_snowflake',
    sql='CALL trading.load_daily_data(\'{{ ds }}\')',
    dag=dag,
)

# Define simple linear flow
extract_task >> process_task >> load_task
