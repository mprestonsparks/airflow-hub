from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="nightly_todo_cleanup",
    schedule_interval="@daily",
    start_date=datetime(2025, 5, 3),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:

    cleanup = BashOperator(
        task_id="run_todo_cleanup",
        bash_command=(
            "docker-compose exec indexagent "
            "bash /app/scripts/maintenance/agent_fix_todos.sh"
        ),
    )