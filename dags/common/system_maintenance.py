"""
System maintenance DAG.

This DAG performs system-wide maintenance tasks that affect all projects,
such as log cleanup, database optimization, and health checks.
"""

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

# Configuration for system maintenance
DEFAULT_ARGS = {
    'owner': 'airflow_admin',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['admin@example.com'],
}

# DAG ID uses 'common' prefix to indicate it's a shared DAG
dag = DAG(
    'common_system_maintenance',
    default_args=DEFAULT_ARGS,
    description='System-wide maintenance tasks',
    schedule_interval='0 0 * * 0',  # Weekly at midnight on Sunday
    start_date=days_ago(1),
    tags=['maintenance', 'system', 'common'],
)
# Use module docstring as DAG documentation
dag.doc_md = __doc__

# Task to clean up old logs
cleanup_logs = BashOperator(
    task_id='cleanup_old_logs',
    bash_command='find /opt/airflow/logs -type f -name "*.log" -mtime +30 -delete',
    dag=dag,
)

# Task to optimize Airflow database
optimize_db = BashOperator(
    task_id='optimize_airflow_db',
    bash_command='airflow db clean --clean-before-timestamp "$(date -d "-30 days" "+%Y-%m-%d")"',
    dag=dag,
)

def check_disk_space(**kwargs):
    """
    Check disk space and log warning if below threshold.
    """
    import os
    import logging
    
    logger = logging.getLogger(__name__)
    from airflow.models import Variable
    
    threshold_gb = Variable.get("system_maintenance_disk_threshold_gb", default_var=10, deserialize_json=False)
    # Ensure threshold_gb is a number
    try:
        threshold_gb = float(threshold_gb)
    except ValueError:
        logger.error(f"Invalid value for system_maintenance_disk_threshold_gb variable: {threshold_gb}. Using default of 10.")
        threshold_gb = 10.0

    # Get disk usage statistics
    stat = os.statvfs('/opt/airflow')
    free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)
    
    if free_gb < threshold_gb:
        logger.warning(f"Low disk space: {free_gb:.2f} GB free, threshold is {threshold_gb} GB")
        kwargs['ti'].xcom_push(key='disk_space_warning', value=True)
        return False
    else:
        logger.info(f"Disk space check passed: {free_gb:.2f} GB free")
        return True

# Task to check disk space
check_disk = PythonOperator(
    task_id='check_disk_space',
    python_callable=check_disk_space,
    dag=dag,
)

def check_connections(**kwargs):
    """
    Check all connections are valid and log any issues.
    """
    import logging
    from airflow.hooks.base import BaseHook
    
    logger = logging.getLogger(__name__)
    connections = BaseHook.get_connections()
    
    failed_connections = []
    
    for conn in connections:
        try:
            # Try to get the connection (this will validate it)
            hook = BaseHook.get_hook(conn_id=conn.conn_id)
            logger.info(f"Connection {conn.conn_id} is valid")
        except Exception as e:
            logger.warning(f"Connection {conn.conn_id} failed validation: {str(e)}")
            failed_connections.append(conn.conn_id)
    
    if failed_connections:
        kwargs['ti'].xcom_push(key='failed_connections', value=failed_connections)
        return False
    else:
        return True

# Task to check connections
check_connections_task = PythonOperator(
    task_id='check_connections',
    python_callable=check_connections,
    dag=dag,
)

# Define task dependencies
cleanup_logs >> optimize_db
check_disk >> check_connections_task
