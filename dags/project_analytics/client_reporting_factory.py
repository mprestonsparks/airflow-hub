"""
Client reporting DAG factory.

This module demonstrates the DAG factory pattern for generating multiple similar DAGs,
one for each client's reporting needs. This approach avoids code duplication while
maintaining clear separation between client-specific workflows.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

# Client configuration
CLIENTS = {
    'client1': {
        'schedule': '0 6 * * *',  # 6:00 AM daily
        'start_date': days_ago(1),
        'email': 'client1@example.com',
        'report_types': ['summary', 'detailed', 'forecast']
    },
    'client2': {
        'schedule': '0 7 * * *',  # 7:00 AM daily
        'start_date': days_ago(1),
        'email': 'client2@example.com',
        'report_types': ['summary', 'detailed']
    },
    'client3': {
        'schedule': '0 8 * * 1-5',  # 8:00 AM weekdays only
        'start_date': days_ago(1),
        'email': 'client3@example.com',
        'report_types': ['summary']
    }
}

# Default arguments for all client DAGs
DEFAULT_ARGS = {
    'owner': 'analytics_team',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'pool': 'project_analytics_pool',
    'email_on_failure': True,
    'email_on_retry': False,
}

def send_email_notification(client_id, report_date, report_types, recipient_email, **kwargs):
    """
    Send email notification when reports are ready.
    
    In a real implementation, this would use Airflow's email functionality or an API.
    For this example, we'll just log the action.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Sending email notification to {recipient_email}")
    logger.info(f"Reports ready for {client_id} for date {report_date}: {', '.join(report_types)}")
    
    # In a real implementation:
    # from airflow.utils.email import send_email
    # send_email(
    #     to=recipient_email,
    #     subject=f"Reports Ready: {client_id} - {report_date}",
    #     html_content=f"Your reports are ready: {', '.join(report_types)}",
    # )
    
    return True

def create_client_dag(client_id, config):
    """
    Create a DAG for a specific client's reporting needs.
    
    Args:
        client_id (str): Client identifier.
        config (dict): Client-specific configuration.
        
    Returns:
        DAG: Configured Airflow DAG for this client.
    """
    dag_id = f"project_analytics_{client_id}_reporting"
    
    dag = DAG(
        dag_id,
        default_args={**DEFAULT_ARGS, 'email': [config['email']]},
        description=f"Daily reporting for {client_id}",
        schedule_interval=config['schedule'],
        start_date=config['start_date'],
        tags=['analytics', 'reporting', client_id],
    )
    
    # Generate reports task
    generate_reports = SnowflakeOperator(
        task_id='generate_client_reports',
        snowflake_conn_id='project_analytics_snowflake',
        sql=f'''
        -- Generate client-specific reports
        CALL analytics.generate_client_reports(
            '{client_id}',
            '{{{{ ds }}}}',
            '{",".join(config["report_types"])}'
        );
        ''',
        dag=dag,
    )
    
    # Export reports task
    export_reports = SnowflakeOperator(
        task_id='export_reports_to_storage',
        snowflake_conn_id='project_analytics_snowflake',
        sql=f'''
        -- Export reports to cloud storage
        CALL analytics.export_client_reports_to_storage(
            '{client_id}',
            '{{{{ ds }}}}'
        );
        ''',
        dag=dag,
    )
    
    # Send notification task
    send_notification = PythonOperator(
        task_id='send_email_notification',
        python_callable=send_email_notification,
        op_kwargs={
            'client_id': client_id,
            'report_date': '{{ ds }}',
            'report_types': config['report_types'],
            'recipient_email': config['email']
        },
        dag=dag,
    )
    
    # Define task dependencies
    generate_reports >> export_reports >> send_notification
    
    return dag

# Create a DAG for each client
for client_id, config in CLIENTS.items():
    globals()[f"{client_id}_dag"] = create_client_dag(client_id, config)
