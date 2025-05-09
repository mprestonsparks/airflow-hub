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
    dag_id='nightly_todo_cleanup',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
    tags=['maintenance', 'todo'],
) as dag:
    run_todo_cleanup = SSHOperator(
        task_id='run_todo_cleanup',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/maintenance/agent_fix_todos.sh',
    )