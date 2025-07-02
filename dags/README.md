# Airflow DAGs Organization

This directory contains Apache Airflow DAGs organized by project to maintain clean separation of concerns and enable independent usage.

## Directory Structure

```
dags/
├── README.md               # This file
├── common/                 # Shared, reusable DAGs
│   ├── system_maintenance.yaml
│   └── nightly_*.py       # Generic maintenance tasks
├── dean/                   # DEAN-specific DAGs
│   ├── dean_*.py          # DEAN workflows
│   └── dean_contracts.py  # DEAN data models
├── project_analytics/      # Analytics project DAGs
├── project_trading/        # Trading project DAGs
├── market-analysis/        # Market analysis DAGs
└── yaml_dag_loader.py     # Dynamic YAML DAG loader
```

## Project Organization Pattern

Each project should be organized in its own subdirectory to maintain independence:

1. **Project Directory**: Create a subdirectory named after your project
2. **Naming Convention**: Prefix DAG files with project identifier (e.g., `projectname_workflow.py`)
3. **Dependencies**: Keep project-specific dependencies within the project directory
4. **Configuration**: Use Airflow Variables/Connections prefixed with project name

## Adding a New Project

1. Create a new directory under `dags/`:
   ```bash
   mkdir dags/my_project
   ```

2. Add project-specific DAGs:
   ```python
   # dags/my_project/my_project_workflow.py
   from airflow import DAG
   from airflow.models import Variable
   
   # Use project-prefixed variables
   project_config = Variable.get("MY_PROJECT_CONFIG", deserialize_json=True)
   ```

3. Configure connections in Airflow UI:
   - Connection ID: `my_project_api`
   - Variables: `MY_PROJECT_*`

## Best Practices

1. **Isolation**: Each project's DAGs should be self-contained
2. **Configuration**: Use Airflow Variables and Connections (never hardcode)
3. **Dependencies**: Document external dependencies in project README
4. **Testing**: Include project-specific tests in `tests/dags/project_name/`

## Independence

The airflow-hub can be used independently by:
- Running only the DAGs you need
- Removing/ignoring project directories you don't use
- Each project directory is completely optional