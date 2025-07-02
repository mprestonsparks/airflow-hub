"""
DEAN Integration Test DAG
Tests the connection between Airflow and DEAN API
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.http_operator import SimpleHttpOperator
from airflow.models import Variable
import requests
import logging

default_args = {
    'owner': 'dean_system',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'dean_test_integration',
    default_args=default_args,
    description='Test DEAN API integration',
    schedule_interval=None,
    catchup=False,
    tags=['dean', 'test']
)

def test_dean_health(**context):
    """Test DEAN API health endpoint"""
    logger = logging.getLogger(__name__)
    
    dean_api_url = Variable.get('dean_api_url', default_var='http://dean-api:8091')
    logger.info(f"Testing DEAN API at: {dean_api_url}")
    
    try:
        response = requests.get(f"{dean_api_url}/health", timeout=10)
        data = response.json()
        logger.info(f"DEAN API Response: {data}")
        
        if response.status_code == 200:
            logger.info("DEAN API is healthy!")
            return data
        else:
            raise Exception(f"DEAN API unhealthy: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to connect to DEAN API: {e}")
        raise

def create_test_agent(**context):
    """Create a test agent via DEAN API"""
    logger = logging.getLogger(__name__)
    
    dean_api_url = Variable.get('dean_api_url', default_var='http://dean-api:8091')
    
    agent_data = {
        "goal": "Test agent from Airflow DAG",
        "token_budget": 1000,
        "diversity_weight": 0.5
    }
    
    try:
        response = requests.post(
            f"{dean_api_url}/api/v1/agents",
            json=agent_data,
            timeout=30
        )
        
        if response.status_code == 200:
            agent = response.json()
            logger.info(f"Created test agent: {agent}")
            context['task_instance'].xcom_push(key='agent_id', value=agent['id'])
            return agent
        else:
            raise Exception(f"Failed to create agent: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"Failed to create agent: {e}")
        raise

def list_agents(**context):
    """List all agents via DEAN API"""
    logger = logging.getLogger(__name__)
    
    dean_api_url = Variable.get('dean_api_url', default_var='http://dean-api:8091')
    
    try:
        response = requests.get(f"{dean_api_url}/api/v1/agents", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Found {data['total']} agents")
            return data
        else:
            raise Exception(f"Failed to list agents: {response.status_code}")
    except Exception as e:
        logger.error(f"Failed to list agents: {e}")
        raise

# Define tasks
test_health = PythonOperator(
    task_id='test_dean_health',
    python_callable=test_dean_health,
    dag=dag,
)

create_agent = PythonOperator(
    task_id='create_test_agent',
    python_callable=create_test_agent,
    dag=dag,
)

list_all_agents = PythonOperator(
    task_id='list_agents',
    python_callable=list_agents,
    dag=dag,
)

# Set task dependencies
test_health >> create_agent >> list_all_agents