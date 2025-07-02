from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import timedelta
import requests
import yaml
import logging

logger = logging.getLogger(__name__)

def call_indexagent_endpoint():
    """Call IndexAgent endpoint for TODO cleanup"""
    # Load configuration from Airflow Variables
    config_path = Variable.get("todo_cleanup_config_path", None)
    
    # Use endpoint from Variable or config file
    if config_path:
        try:
            with open(config_path, 'r') as file:
                config = yaml.safe_load(file)
            endpoint_url = config.get('endpoint_url', Variable.get("indexagent_url", "http://localhost:8081"))
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}. Using default.")
            endpoint_url = Variable.get("indexagent_url", "http://localhost:8081")
    else:
        endpoint_url = Variable.get("indexagent_url", "http://localhost:8081")
    
    # Build full URL
    url = f"{endpoint_url}/api/v1/actions/fix-todos"
    
    # Make request with auth if configured
    headers = {}
    api_key = Variable.get("indexagent_api_key", None)
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    logger.info(f"Calling IndexAgent endpoint: {url}")
    response = requests.post(url, headers=headers, json={"auto_commit": True})
    
    if response.status_code != 200:
        raise Exception(f"Failed to call IndexAgent endpoint: {response.status_code} - {response.text}")
    
    logger.info(f"IndexAgent response: {response.json()}")
    return response.json()

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
        bash_command="""
            ssh {{ var.value.deployment_ssh_user }}@{{ var.value.deployment_ssh_host }} \
            "bash {{ var.value.deployment_scripts_path }}/agent_fix_todos.sh"
        """.strip(),
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