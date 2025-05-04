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
    dag_id='nightly_doc_refresh',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@daily',
    catchup=False,
    tags=['maintenance', 'docs'],
) as dag:
    scan_undoc = SSHOperator(
        task_id='scan_undoc',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/documentation/find_undocumented.py',
    )

    generate_docs = SSHOperator(
        task_id='generate_docs',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/documentation/agent_write_docs.sh',
    )

    docs_coverage = SSHOperator(
        task_id='update_docs_coverage',
        ssh_conn_id='indexagent_ssh',
        command='/opt/indexagent/scripts/documentation/update_docs_coverage.sh',
    )

    scan_undoc >> generate_docs >> docs_coverage