#!/bin/bash

# Airflow Hub Post-Create Script
# This script runs after the container is created

set -e

echo "🚀 Setting up Airflow Hub development environment..."

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Set up Airflow environment variables
export AIRFLOW_HOME=/workspaces/airflow-hub
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@host.docker.internal:5432/airflow
export AIRFLOW__CORE__EXECUTOR=LocalExecutor
export AIRFLOW__CORE__LOAD_EXAMPLES=false
export AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=true
export AIRFLOW__WEBSERVER__EXPOSE_CONFIG=true

# =============================================================================
# DIRECTORY STRUCTURE
# =============================================================================

echo "📁 Creating Airflow directory structure..."

# Create Airflow directories
mkdir -p dags
mkdir -p logs
mkdir -p plugins
mkdir -p config
mkdir -p tests
mkdir -p scripts

# Create subdirectories for organization
mkdir -p dags/examples
mkdir -p dags/utils
mkdir -p plugins/operators
mkdir -p plugins/sensors
mkdir -p plugins/hooks
mkdir -p config/connections
mkdir -p tests/dags
mkdir -p tests/plugins

echo "✅ Directory structure created"

# =============================================================================
# AIRFLOW CONFIGURATION
# =============================================================================

echo "⚙️ Setting up Airflow configuration..."

# Create airflow.cfg if it doesn't exist
if [ ! -f "airflow.cfg" ]; then
    echo "📝 Generating Airflow configuration..."
    airflow config list > /dev/null 2>&1 || echo "Airflow config initialized"
fi

# Create requirements.txt if it doesn't exist
if [ ! -f "requirements.txt" ]; then
    echo "📝 Creating requirements.txt..."
    cat > requirements.txt << EOF
# Airflow Core
apache-airflow[postgres,vault,docker]==3.0.0

# Database connectors
psycopg2-binary>=2.9.0
sqlalchemy>=1.4.0

# Vault integration
hvac>=1.0.0

# Development tools
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
ruff>=0.1.0

# Utilities
python-dotenv>=1.0.0
requests>=2.28.0
httpx>=0.24.0
pandas>=2.0.0
EOF
fi

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "📦 Installing Python dependencies..."
    pip install --user -r requirements.txt
fi

echo "✅ Airflow configuration complete"

# =============================================================================
# SAMPLE DAG CREATION
# =============================================================================

echo "📄 Creating sample DAGs..."

# Create a sample DAG if dags directory is empty
if [ ! "$(ls -A dags/)" ]; then
    cat > dags/sample_dag.py << 'EOF'
"""
Sample Airflow DAG for development and testing
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

# Default arguments
default_args = {
    'owner': 'airflow-hub',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    'sample_dag',
    default_args=default_args,
    description='A sample DAG for development',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sample', 'development'],
)

def print_context(**context):
    """Print the Airflow context"""
    print(f"Execution date: {context['execution_date']}")
    print(f"DAG run ID: {context['dag_run'].run_id}")
    return "Context printed successfully"

# Define tasks
t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

t2 = PythonOperator(
    task_id='print_context',
    python_callable=print_context,
    dag=dag,
)

t3 = BashOperator(
    task_id='sleep',
    bash_command='sleep 5',
    dag=dag,
)

# Set task dependencies
t1 >> t2 >> t3
EOF

    echo "✅ Sample DAG created"
fi

# =============================================================================
# TESTING SETUP
# =============================================================================

echo "🧪 Setting up testing framework..."

# Create pytest configuration
if [ ! -f "pytest.ini" ]; then
    cat > pytest.ini << EOF
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=dags
    --cov=plugins
    --cov-report=term-missing
    --cov-report=html:htmlcov
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
EOF
fi

# Create sample test
if [ ! -f "tests/test_sample_dag.py" ]; then
    cat > tests/test_sample_dag.py << 'EOF'
"""
Tests for sample DAG
"""
import pytest
from datetime import datetime
from airflow.models import DagBag

def test_dag_loaded():
    """Test that the sample DAG is loaded correctly"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='sample_dag')
    assert dag is not None
    assert len(dag.tasks) == 3

def test_dag_structure():
    """Test the DAG structure"""
    dagbag = DagBag()
    dag = dagbag.get_dag(dag_id='sample_dag')
    
    # Check task IDs
    task_ids = [task.task_id for task in dag.tasks]
    expected_tasks = ['print_date', 'print_context', 'sleep']
    assert set(task_ids) == set(expected_tasks)
    
    # Check dependencies
    print_date_task = dag.get_task('print_date')
    print_context_task = dag.get_task('print_context')
    sleep_task = dag.get_task('sleep')
    
    assert print_context_task in print_date_task.downstream_list
    assert sleep_task in print_context_task.downstream_list
EOF
fi

echo "✅ Testing framework setup complete"

# =============================================================================
# DEVELOPMENT TOOLS
# =============================================================================

echo "🛠️ Setting up development tools..."

# Create Makefile for common tasks
if [ ! -f "Makefile" ]; then
    cat > Makefile << 'EOF'
.PHONY: help test lint format check-dags init-db start-webserver start-scheduler

help:
	@echo "Available commands:"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  format        - Format code"
	@echo "  check-dags    - Check DAG syntax"
	@echo "  init-db       - Initialize Airflow database"
	@echo "  start-webserver - Start Airflow webserver"
	@echo "  start-scheduler - Start Airflow scheduler"

test:
	pytest tests/

lint:
	ruff check dags/ plugins/ tests/
	mypy dags/ plugins/ || true

format:
	black dags/ plugins/ tests/
	ruff check --fix dags/ plugins/ tests/

check-dags:
	python -m py_compile dags/*.py
	airflow dags list

init-db:
	airflow db init
	airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com \
		--password admin

start-webserver:
	airflow webserver --port 8080

start-scheduler:
	airflow scheduler
EOF
fi

# Create .gitignore if it doesn't exist
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Airflow
airflow.cfg
airflow.db
airflow-webserver.pid
logs/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
EOF
fi

echo "✅ Development tools setup complete"

# =============================================================================
# COMPLETION
# =============================================================================

echo ""
echo "🎉 Airflow Hub setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Wait for PostgreSQL to be available"
echo "   2. Run 'make init-db' to initialize the Airflow database"
echo "   3. Run 'make start-webserver' to start the Airflow UI"
echo "   4. Access Airflow at http://localhost:8080 (admin/admin)"
echo ""
echo "🔧 Available commands:"
echo "   - 'make help' to see all available commands"
echo "   - 'make test' to run tests"
echo "   - 'make check-dags' to validate DAG syntax"
echo "   - 'airflow dags list' to see available DAGs"
echo ""
echo "Happy DAG development! 🚀"