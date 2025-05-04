from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import requests

import yaml

def call_indexagent_endpoint():
    # Load configuration from config.yaml
    with open('/path/to/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
    url = config['endpoint_url']
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to call IndexAgent endpoint: {response.text}")

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'nightly_todo_cleanup',
    default_args=default_args,
    description='A DAG to clean up TODOs nightly',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['cleanup', 'nightly'],
) as dag:

    # Task to SSH-exec the script
    ssh_exec_task = BashOperator(
        task_id='ssh_exec_agent_fix_todos',
        bash_command='ssh user@host "bash /path/to/agent_fix_todos.sh"',
    )

    # Task to call the IndexAgent endpoint
    call_endpoint_task = PythonOperator(
        task_id='call_indexagent_endpoint',
        python_callable=call_indexagent_endpoint,
    )

    # Choose one of the tasks to execute
    # Uncomment the desired task to execute
    # ssh_exec_task
    call_endpoint_task