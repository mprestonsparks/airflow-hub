# Airflow Monorepo Architecture Guidelines

These guidelines outline how to architect a single Airflow repository that coordinates multiple, diverse projects (trading systems, AI toolchains, CRMs, bookkeeping apps, etc.) while maintaining modularity, scalability, and multi-tenancy support. The repository structure is designed to be easily maintainable for solo developers, compatible with AI-powered assistants, and scalable as systems evolve.

## 1. Repository Architecture: Monorepo Approach

We'll use a **monorepo with a single Airflow instance** as our starting point, based on these considerations:

- **Centralized Management**: One deployment pipeline and single view of all workflows
- **Code Reuse**: Shared libraries and plugins across projects
- **Simplified Operations**: Avoids duplicated infrastructure
- **Future Flexibility**: Repository structure allows migrating specific projects to separate Airflow instances if needed later

### Repository Structure

```
airflow-monorepo/
├── dags/
│   ├── project_a/
│   │   ├── dag_project_a_task1.py
│   │   ├── resources/
│   │   │   └── (SQL templates, config files)
│   │   └── __init__.py
│   ├── project_b/
│   │   └── ...
│   └── common/          # (Optional) shared DAG-level logic
│
├── plugins/
│   ├── common/          # Reusable code across projects
│   │   ├── hooks/
│   │   ├── operators/
│   │   ├── utils.py
│   │   └── __init__.py
│   ├── project_a/       # Project-specific logic
│   │   └── custom_ops.py
│   └── project_b/
│       └── ...
│
├── tests/
│   ├── common/
│   ├── project_a/
│   ├── project_b/
│   └── test_dag_validation.py
│
├── requirements.txt     # Single environment approach
├── docker/              # For containerized approach
│   ├── Dockerfile.airflow
│   └── project_specific/
│       ├── Dockerfile.project_a
│       └── Dockerfile.project_b
├── .airflowignore       # Patterns to exclude from DAG parsing
└── README.md
```

### Potential Challenges & Mitigations

- **Scheduler Bottleneck**: As DAG count grows, scheduler performance can degrade. Mitigate by keeping DAGs lean and using nested directories with clear project boundaries
- **Dependency Conflicts**: Projects might need different library versions. Address using containerized task approach (details in Section 4)
- **Single Point of Failure**: All projects affected by Airflow outage. Mitigate with robust monitoring and automated recovery

## 2. DAG Organization

### Use Nested Directory Structure 

Rather than a flat structure (all DAGs in one directory), organize DAGs by project:

```python
# Example structure for a project DAG
# File: dags/project_a/daily_sync_dag.py

from airflow import DAG
from datetime import datetime
from plugins.common.hooks import CommonHook
from plugins.project_a.operators import ProjectAOperator

dag = DAG(
    'project_a_daily_sync',  # Prefixed ID for clear identification
    schedule_interval='@daily',
    start_date=datetime(2023, 1, 1)
)

task1 = ProjectAOperator(
    task_id='extract_data',
    conn_id='project_a_source_db',  # Project-specific connection
    dag=dag
)

# ... rest of DAG definition
```

### Naming Conventions

- **DAG IDs**: Prefix with project name: `project_a_daily_task`
- **File Names**: Clear, descriptive: `dag_project_a_daily_sync.py`
- **Tasks**: Meaningful names describing the function: `extract_data`, `transform_records`

### DAG File Guidelines

- Keep DAG files *declarative* - primarily defining:
  - Schedule intervals
  - Task dependencies
  - References to operators/hooks
- Move *implementation logic* to plugins or modules
- Use `.airflowignore` to prevent Airflow from parsing non-DAG files
- Include project-specific resources (SQL templates, config) in a `resources/` subfolder

## 3. Shared Code & Modularity

### Plugins Structure

Store reusable code in organized modules:

```python
# Example of a common hook in plugins/common/hooks/api_hook.py
from airflow.hooks.base import BaseHook

class CommonAPIHook(BaseHook):
    def __init__(self, conn_id):
        self.conn_id = conn_id
        self.connection = self.get_connection(conn_id)
        # Connection details are stored in Airflow, not hardcoded
        self.api_key = self.connection.password
        self.api_url = self.connection.host
    
    def call_api(self, endpoint, params=None):
        """Common API functionality used across projects"""
        # Implementation details...
```

### Project Boundaries

- **No Cross-Project Dependencies**: A project's DAGs should only import from:
  - Core Airflow libraries
  - `plugins/common/` modules
  - Its own project module (`plugins/project_a/`)
- **Example correct import** (from a Project A DAG):
  ```python
  from plugins.common.hooks import CommonHook
  from plugins.project_a.operators import CustomOperator
  # NEVER: from plugins.project_b import anything
  ```

- **Moving Shared Logic**: If multiple projects need similar functionality, refactor it into the common module:
  ```python
  # Instead of copying code between projects, move to common:
  from plugins.common.transformers import DataCleaner
  ```

## 4. Dependency Management

Choose one of these approaches based on project complexity:

### Approach 1: Single Environment 

- One `requirements.txt` with all dependencies
- Pin versions to avoid conflicts
- Used when projects have compatible library needs
- Example:
  ```
  # requirements.txt
  apache-airflow==2.5.1
  pandas==1.5.3
  snowflake-connector-python==3.0.2
  # etc.
  ```

### Approach 2: Containerized Tasks

- Each project defines its own dependencies in isolated environments
- Use `KubernetesPodOperator` or `DockerOperator` to run tasks
- Example DAG:
  ```python
  # Using containerized tasks for isolated dependencies
  from airflow.providers.docker.operators.docker import DockerOperator
  
  task = DockerOperator(
      task_id='project_a_process',
      image='trading-project:latest',  # Project-specific Docker image
      command='python /scripts/process.py',
      environment={
          'PROJECT_ENV': 'production',
          'CONN_ID': 'project_a_db'  # Project-specific connection
      },
      dag=dag
  )
  ```

- Example Dockerfile for a project:
  ```dockerfile
  # docker/project_specific/Dockerfile.project_a
  FROM python:3.9-slim
  
  WORKDIR /app
  COPY ./requirements_project_a.txt .
  RUN pip install -r requirements_project_a.txt
  
  COPY ./plugins/project_a /app/project_a
  COPY ./plugins/common /app/common
  
  ENTRYPOINT ["python"]
  ```

## 5. Multi-Tenancy & Isolation

### Logical Isolation Strategies

Since one Airflow instance serves multiple projects, use these isolation techniques:

#### Resource Namespacing

- **Connections**: `project_a_db`, `project_b_api`
- **Variables**: `project_a_settings`, `project_b_config`
- **Pool Names**: `project_a_pool`, `project_b_pool`

#### Access Control

- Use Airflow's RBAC to limit UI access by project
- Example role configuration:
  ```python
  # In a setup script or admin interface
  from airflow.models import DagBag
  from airflow.www.security import AirflowSecurityManager
  
  # Create role for Project A users
  security_manager.add_role("project_a_user")
  
  # Grant permissions only to Project A DAGs
  for dag_id in DagBag().dag_ids:
      if dag_id.startswith("project_a_"):
          security_manager.add_permission_role(
              security_manager.find_role("project_a_user"),
              security_manager.get_action("can_read"),
              dag_id
          )
  ```

#### Resource Allocation

- Use Airflow pools to partition executor resources by project
- Configure in the Airflow UI or via environment variables:
  ```
  AIRFLOW__POOLS__PROJECT_A_POOL=10  # 10 slots for Project A tasks
  AIRFLOW__POOLS__PROJECT_B_POOL=5   # 5 slots for Project B tasks
  ```
- Assign tasks to pools in DAG definition:
  ```python
  task = MyOperator(
      task_id='task1',
      pool='project_a_pool',
      # ...
  )
  ```

### When to Consider Multiple Airflow Instances

For projects requiring strict isolation (high security, different scaling needs), be prepared to spin up separate Airflow instances:

- Keep modular structure so it's easy to extract one project's DAGs
- Consider using a deployment tool that can target multiple Airflow instances

## 6. Secrets & Configuration Management

### External Secrets Management

- **Never store credentials in repository**
- Use Airflow's support for external secrets backends:
  - HashiCorp Vault
  - AWS Secrets Manager
  - GCP Secret Manager

```python
# Example Airflow configuration for secrets backend (airflow.cfg or env vars)
AIRFLOW__SECRETS__BACKEND = "airflow.providers.hashicorp.secrets.vault.VaultBackend"
AIRFLOW__SECRETS__BACKEND_KWARGS = {
    "connections_path": "airflow/connections",
    "variables_path": "airflow/variables",
    "mount_point": "secret",
    "url": "http://vault:8200"
}
```

### Connection Referencing

- Each project defines its required connections using project-specific naming
- Document these requirements in each project's README:

```
Required Connections for Project A:
- project_a_db: Snowflake connection with read/write access to analytics schema
- project_a_api: HTTP connection to external data provider
```

- Reference in DAGs:
```python
task = SnowflakeOperator(
    task_id='load_data',
    conn_id='project_a_db',  # Project-specific connection ID
    sql='SELECT * FROM my_table',
    dag=dag
)
```

## 7. CI/CD & Quality Assurance

### Continuous Integration Pipeline

Implement CI checks for DAG changes:

1. **Linting**: Use `pylint` or `flake8` with Airflow plugins
2. **DAG Validation**: Test DAG parsing without executing
   ```python
   # tests/test_dag_validation.py
   import pytest
   from airflow.models import DagBag
   
   def test_dag_loading():
       dag_bag = DagBag(include_examples=False)
       assert not dag_bag.import_errors, f"DAG import errors: {dag_bag.import_errors}"
       
       # Verify Project A DAGs exist
       project_a_dags = [dag_id for dag_id in dag_bag.dag_ids if dag_id.startswith('project_a_')]
       assert len(project_a_dags) > 0, "No Project A DAGs found"
   ```

3. **Unit Tests**: Test plugins and operators
   ```python
   # tests/project_a/test_operators.py
   from plugins.project_a.operators import ProjectAOperator
   
   def test_project_a_operator():
       operator = ProjectAOperator(
           task_id='test_task',
           conn_id='test_conn'
       )
       # Test operator functionality
   ```

### Deployment Strategy

For a single Airflow instance:

1. Git-based deployment:
   ```bash
   # Example deployment script
   git pull origin main
   pip install -r requirements.txt
   systemctl restart airflow-webserver airflow-scheduler
   ```

2. Container-based deployment:
   ```bash
   # Build main Airflow image
   docker build -f docker/Dockerfile.airflow -t airflow:latest .
   
   # Build project-specific images
   docker build -f docker/project_specific/Dockerfile.project_a -t project-a:latest .
   
   # Deploy with Docker Compose or Kubernetes
   ```

## 8. Scalability Considerations

### Monitoring & Performance

- Monitor scheduler performance as DAG count grows
- Keep an eye on:
  - DAG parse time
  - Task execution latency
  - Worker resource utilization
- Consider splitting high-demand projects to separate Airflow instances if needed

### DAG Factory Pattern

For multiple similar DAGs, use the DAG factory pattern:

```python
# Example DAG factory for multiple similar client DAGs
def create_client_dag(client_id, schedule, start_date):
    dag = DAG(
        f'project_a_{client_id}_daily',
        schedule_interval=schedule,
        start_date=start_date
    )
    
    task1 = ExtractionOperator(
        task_id=f'extract_{client_id}',
        client_id=client_id,
        dag=dag
    )
    
    task2 = TransformOperator(
        task_id=f'transform_{client_id}',
        client_id=client_id,
        dag=dag
    )
    
    task1 >> task2
    return dag

# Generate DAGs for multiple clients
for client in ['client1', 'client2', 'client3']:
    globals()[f'{client}_dag'] = create_client_dag(
        client_id=client,
        schedule='@daily',
        start_date=datetime(2023, 1, 1)
    )
```

### Big Data Integration

For big data workloads:
- Use containerized tasks with specialized images
- Consider separate deployment for heavy processing:

```python
# Example integrating with external Spark cluster
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator

spark_task = SparkSubmitOperator(
    task_id='process_large_dataset',
    application='/path/to/script.py',
    conn_id='spark_conn',
    total_executor_cores=4,
    executor_memory='2g',
    dag=dag
)
```

## 9. AI-Assisted Development Best Practices

When working with AI coding agents like Cascade:

### Documentation Guidelines

- **Clear Task Boundaries**: Document where each project starts/ends
- **Interface Documentation**: Describe expected inputs/outputs
- **Code Comments**: Include reasoning behind design decisions

```python
# Example well-documented code for AI assistance
class ProjectAOperator(BaseOperator):
    """
    Operator for Project A data processing.
    
    This operator connects to the source system via the specified connection ID,
    extracts data based on the provided parameters, and returns it in a standardized
    format for downstream tasks.
    
    Args:
        conn_id (str): Connection ID for the source system. Must be configured in 
                       Airflow with the project_a_ prefix.
        extract_date (str): Date to extract data for in YYYY-MM-DD format.
    """
    def __init__(self, conn_id, extract_date, **kwargs):
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.extract_date = extract_date
        
        # Validate inputs for better error messages
        if not conn_id.startswith('project_a_'):
            self.log.warning("Connection ID should follow project naming convention: project_a_*")
```

### Testing for AI-Generated Code

- Create robust test fixtures that AI can reference
- Add examples of expected inputs/outputs
- Include edge case handling

## 10. Implementation Example: Trading System DAG

Complete example of a properly structured trading system DAG:

```python
# dags/project_trading/trading_daily_sync.py
from airflow import DAG
from airflow.utils.dates import days_ago
from plugins.common.hooks import DatabaseHook
from plugins.project_trading.operators import IBKRDataOperator

# Configuration should follow project naming conventions
DEFAULT_ARGS = {
    'owner': 'trading_team',
    'depends_on_past': False,
    'retries': 3,
    'pool': 'project_trading_pool',  # Project-specific resource pool
}

# DAG ID has project prefix for clear identification
dag = DAG(
    'project_trading_daily_sync',
    default_args=DEFAULT_ARGS,
    description='Syncs daily trading data from IBKR to data warehouse',
    schedule_interval='0 1 * * *',
    start_date=days_ago(1),
    tags=['trading', 'ibkr'],
)

# Using project-specific operator with clear task ID
extract_task = IBKRDataOperator(
    task_id='extract_ibkr_data',
    conn_id='project_trading_ibkr',  # Project-specific connection
    data_types=['trades', 'positions'],
    dag=dag,
)

# Processing task using containerized execution for dependency isolation
process_task = DockerOperator(
    task_id='process_trading_data',
    image='trading-project:latest',
    command='python /scripts/process_trading_data.py',
    environment={
        'DATA_DATE': '{{ ds }}',
        'DATA_PATH': '/tmp/data/{{ ds }}',
    },
    dag=dag,
)

# Data load task with project-specific connection
load_task = SnowflakeOperator(
    task_id='load_processed_data',
    conn_id='project_trading_snowflake',
    sql='CALL trading.load_daily_data(\'{{ ds }}\')',
    dag=dag,
)

# Define simple linear flow
extract_task >> process_task >> load_task
```

## Conclusion

This monorepo structure balances modularity with shared infrastructure, enabling diverse projects to coexist while maintaining clear boundaries. The approach allows for:

- Independent project evolution
- Code reuse across projects
- Clear ownership and organization
- Simplified operations with a single Airflow instance
- Future flexibility to migrate projects if needed

Follow these guidelines to ensure your Airflow monorepo remains maintainable, modular, and scalable as your portfolio of orchestrated projects grows.