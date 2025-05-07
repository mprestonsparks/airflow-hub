from airflow import DAG
from airflow.providers.ssh.operators.ssh import SSHOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow_admin',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'email_on_failure': True,
    'email': ['admin@example.com'],
}

with DAG(
    dag_id='nightly_test_improve',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
    tags=['maintenance', 'test'],
) as dag:
    run_cov = SSHOperator(
        task_id='run_cov',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/run_cov.py',
    )
    ai_test_loop = SSHOperator(
        task_id='ai_test_loop',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/testing/ai_test_loop.sh',
    )