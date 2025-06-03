# Airflow Monorepo Hub

A centralized monorepo architecture for managing multiple Airflow projects while maintaining modularity, scalability, and multi-tenancy support.

## Overview

This repository follows a monorepo approach with a single Airflow instance that coordinates multiple, diverse projects (trading systems, analytics pipelines, data processing workflows, etc.) while maintaining clear project boundaries and code organization.

## Repository Structure

```
airflow-hub/
├── dags/                  # All DAG definitions organized by project
│   ├── project_trading/   # Trading system DAGs
│   ├── project_analytics/ # Analytics DAGs
│   └── common/            # Shared DAG-level logic
│
├── plugins/               # Reusable code and project-specific modules
│   ├── common/            # Shared code across all projects
│   ├── project_trading/   # Trading-specific operators and hooks
│   └── project_analytics/ # Analytics-specific operators and hooks
│
├── tests/                 # Testing infrastructure
│   ├── dags/              # DAG tests
│   └── plugins/           # Plugin tests
│
├── docker/                # Containerization configuration
│   ├── Dockerfile.airflow # Main Airflow image (base environment)
│   └── project_specific/  # Optional, project-specific Dockerfiles/images
│                        # Use when projects have complex or conflicting dependencies
│
├── requirements.txt       # Core Airflow dependencies for the base image
└── .airflowignore        # Patterns to exclude from DAG parsing (e.g., broken/dev DAGs)
```

## Development Environment Setup

### Option 1: Multi-Repository Dev Container (Recommended)

For integrated development across all repositories, use the multi-repository Dev Container workspace:

1. **Prerequisites:**
   - [VSCode](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   - [Docker Desktop](https://www.docker.com/products/docker-desktop/)

2. **Setup:**
   ```bash
   # Ensure all repositories are cloned as siblings
   ~/Documents/gitRepos/
     ├── airflow-hub/
     ├── IndexAgent/
     ├── market-analysis/
     └── infra/
   
   # Open the parent directory in VSCode
   code ~/Documents/gitRepos
   
   # Select "Reopen in Container" and choose the workspace configuration
   ```

3. **Benefits:**
   - Integrated development environment with all repositories
   - Shared PostgreSQL database with multiple schemas
   - Vault integration for secrets management
   - Port 8080 for Airflow UI access
   - Cross-repository communication and testing

### Option 2: Standalone Dev Container

For Airflow-only development:

1. **Quick Start:**
   ```bash
   git clone https://github.com/mprestonsparks/airflow-hub.git
   cd airflow-hub
   code .
   # VSCode will prompt to "Reopen in Container" - click it!
   ```

2. **Container Features:**
   - Apache Airflow 3.0 with PostgreSQL backend
   - Pre-configured development tools and dependencies
   - Automatic database initialization
   - Port forwarding for web UI access

## Getting Started

### Multi-Repository Workspace Development

When using the multi-repository workspace:

1. **Access Airflow UI:** http://localhost:8080
   - Username: `admin`
   - Password: `admin`

2. **Database Access:**
   ```bash
   # Connect to Airflow database
   psql -h postgres -U airflow -d airflow
   
   # List all databases
   psql -h postgres -U airflow -c "\l"
   ```

3. **DAG Development:**
   ```bash
   # Navigate to airflow-hub
   cd /workspaces/airflow-hub
   
   # List DAGs
   airflow dags list
   
   # Test DAG
   airflow dags test your_dag_id 2024-01-01
   ```

4. **Cross-Repository Integration:**
   ```bash
   # Access other repositories
   cd /workspaces/IndexAgent      # Port 8081
   cd /workspaces/market-analysis # Port 8000
   cd /workspaces/infra          # Infrastructure tools
   ```

### Standalone Development

For traditional Docker Compose setup:

1. **Clone and Setup:**
   ```bash
   git clone https://github.com/mprestonsparks/airflow-hub.git
   cd airflow-hub
   ```

2. **Build and Start:**
   ```bash
   docker-compose build
   docker-compose run --rm airflow-init
   docker-compose up -d
   ```

3. **Verify Installation:**
   ```bash
   docker-compose exec airflow-webserver airflow dags list
   docker-compose exec airflow-webserver airflow dags list-import-errors
   ```

4. **Access Services:**
   - Airflow UI: http://localhost:8080 (login: airflow / airflow)

## DAG Development Workflow

### Creating New DAGs

1. **Project Structure:**
   ```bash
   # Create project directories
   mkdir -p dags/project_new
   mkdir -p plugins/project_new
   mkdir -p tests/dags/project_new
   mkdir -p tests/plugins/project_new
   ```

2. **DAG Template:**
   ```python
   from datetime import datetime, timedelta
   from airflow import DAG
   from airflow.operators.python import PythonOperator
   
   default_args = {
       'owner': 'project_new',
       'depends_on_past': False,
       'start_date': datetime(2024, 1, 1),
       'email_on_failure': False,
       'email_on_retry': False,
       'retries': 1,
       'retry_delay': timedelta(minutes=5),
   }
   
   dag = DAG(
       'project_new_example',
       default_args=default_args,
       description='Example DAG for new project',
       schedule_interval=timedelta(days=1),
       catchup=False,
       tags=['project_new'],
   )
   ```

### Testing DAGs

```bash
# Test DAG syntax
python dags/project_new/example_dag.py

# Test DAG in Airflow
airflow dags test project_new_example 2024-01-01

# Test specific task
airflow tasks test project_new_example task_id 2024-01-01

# Run full test suite
pytest tests/dags/project_new/
```

## Database Integration

### Multi-Database Setup

The workspace provides multiple PostgreSQL databases:

- **airflow**: Airflow metadata and task history
- **indexagent**: IndexAgent application data
- **market_analysis**: Market analysis service data

### Connection Configuration

```python
# In DAGs, use connection IDs
from airflow.hooks.postgres_hook import PostgresHook

# Airflow metadata database
airflow_hook = PostgresHook(postgres_conn_id='postgres_default')

# IndexAgent database
indexagent_hook = PostgresHook(postgres_conn_id='indexagent_db')

# Market analysis database
market_hook = PostgresHook(postgres_conn_id='market_analysis_db')
```

### Database Operations

```bash
# Create new database
psql -h postgres -U airflow -c "CREATE DATABASE new_project;"

# Grant permissions
psql -h postgres -U airflow -c "GRANT ALL PRIVILEGES ON DATABASE new_project TO airflow;"

# Run migrations
cd /workspaces/airflow-hub
alembic upgrade head
```

## Vault Integration

### Secrets Management

The workspace includes HashiCorp Vault for secure secrets management:

```python
# Access secrets in DAGs
from airflow.models import Variable

# Get API keys from Vault
api_key = Variable.get("binance_api_key")
secret_key = Variable.get("binance_secret_key")
```

### Vault Operations

```bash
# Check Vault status
vault status

# Store secrets
vault kv put secret/api-keys \
  binance_api_key="your_key" \
  binance_secret_key="your_secret"

# Read secrets
vault kv get secret/api-keys
```

## API Documentation

### Airflow REST API

Access the Airflow REST API at http://localhost:8080/api/v1/

**Common Endpoints:**

```bash
# List DAGs
curl -X GET "http://localhost:8080/api/v1/dags" \
  -H "Authorization: Basic YWRtaW46YWRtaW4="

# Trigger DAG run
curl -X POST "http://localhost:8080/api/v1/dags/project_new_example/dagRuns" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic YWRtaW46YWRtaW4=" \
  -d '{"conf": {}}'

# Get DAG run status
curl -X GET "http://localhost:8080/api/v1/dags/project_new_example/dagRuns" \
  -H "Authorization: Basic YWRtaW46YWRtaW4="
```

### Cross-Service Communication

```python
# Call IndexAgent API from DAG
import requests

def call_indexagent():
    response = requests.get("http://indexagent:8081/health")
    return response.json()

# Call Market Analysis API
def call_market_analysis():
    response = requests.post(
        "http://market-analysis:8000/analyze",
        json={"symbol": "AAPL", "days": 30}
    )
    return response.json()
```

## Running Tests

### Unit Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/dags/test_example_dag.py

# Run with coverage
pytest --cov=dags --cov=plugins tests/
```

### Integration Tests

```bash
# Test DAG imports
python -c "import dags.project_new.example_dag"

# Test database connections
airflow connections test postgres_default

# Test Vault integration
vault kv get secret/api-keys
```

### Docker Test Environment

```bash
# Run tests in isolated environment
docker-compose up --build --abort-on-container-exit --exit-code-from airflow-test airflow-test
```

## Troubleshooting

### Common Issues

**DAG Import Errors:**
```bash
# Check import errors
airflow dags list-import-errors

# Test DAG syntax
python dags/your_dag.py
```

**Database Connection Issues:**
```bash
# Test PostgreSQL connectivity
pg_isready -h postgres -p 5432 -U airflow

# Check database logs
docker logs airflow-hub_postgres_1
```

**Port Conflicts:**
- Airflow UI: Port 8080
- Ensure no other services are using this port
- Check Docker port mappings: `docker ps`

**Memory Issues:**
```bash
# Check container resource usage
docker stats

# Increase Docker memory allocation in Docker Desktop settings
```

**Vault Access Issues:**
```bash
# Verify Vault token
export VAULT_TOKEN=dev-token
vault auth -method=token

# Check Vault logs
docker logs airflow-hub_vault_1
```

### Performance Optimization

**DAG Performance:**
- Use appropriate `schedule_interval` settings
- Implement proper task dependencies
- Use connection pooling for database operations
- Monitor task execution times in Airflow UI

**Resource Management:**
- Configure appropriate worker pools
- Set task concurrency limits
- Use resource pools for task isolation
- Monitor system resources during peak loads

## Project Management

### Adding a New Project

1. **Create Project Structure:**
   ```bash
   mkdir -p dags/project_new
   mkdir -p plugins/project_new
   mkdir -p tests/dags/project_new
   mkdir -p tests/plugins/project_new
   ```

2. **Configure Connections:**
   - Navigate to Airflow UI → Admin → Connections
   - Add project-specific connections:
     - `project_new_db`
     - `project_new_api`

3. **Create Resource Pool:**
   - Navigate to Airflow UI → Admin → Pools
   - Create pool: `project_new_pool`
   - Set appropriate slot allocation

4. **Environment Variables:**
   ```bash
   # Add to .env file
   PROJECT_NEW_API_KEY=your_api_key
   PROJECT_NEW_DATABASE_URL=postgresql://user:pass@host:port/db
   ```

### Project Isolation

- **Namespace Conventions:**
  - DAG IDs: `project_new_*`
  - Connection IDs: `project_new_*`
  - Variable names: `project_new_*`
  - Pool names: `project_new_pool`

- **Resource Allocation:**
  - Use Airflow pools for task concurrency control
  - Separate database schemas for data isolation
  - Project-specific Docker images when needed

## Contributing

### Development Guidelines

1. **Code Standards:**
   - Follow PEP 8 for Python code
   - Use type hints for function signatures
   - Include comprehensive docstrings
   - Write unit tests for all DAGs and plugins

2. **DAG Guidelines:**
   - Use descriptive DAG and task IDs
   - Include appropriate tags for categorization
   - Set reasonable default arguments
   - Implement proper error handling

3. **Testing Requirements:**
   - Unit tests for all custom operators and hooks
   - Integration tests for DAG workflows
   - Performance tests for resource-intensive tasks

4. **Documentation:**
   - Update README for new features
   - Document API changes
   - Include usage examples

### Pull Request Process

1. Create feature branch from `main`
2. Implement changes with tests
3. Update documentation
4. Submit pull request with detailed description
5. Address review feedback
6. Merge after approval

## License

This project is the private property of M. Preston Sparks. All rights reserved.
