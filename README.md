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

## Getting Started

### Quickstart (Docker Compose)

Prerequisites:
- Docker & Docker Compose installed

1. Clone this repository:
   ```bash
   git clone https://github.com/mprestonsparks/airflow-hub.git
   cd airflow-hub
   ```

2. Build all images:
   ```bash
   docker-compose build
   ```

3. Initialize the Airflow environment (runs DB migrations, creates default user):
   ```bash
   docker-compose run --rm airflow-init
   ```

4. Start Airflow services:
   ```bash
   docker-compose up -d
   ```

5. Verify DAGs imported:
   ```bash
   docker-compose exec airflow-webserver airflow dags list
   docker-compose exec airflow-webserver airflow dags list-import-errors
   ```
   
### Running Tests

You can run all DAG and plugin tests in an isolated Airflow environment:
```bash
docker-compose up --build --abort-on-container-exit --exit-code-from airflow-test airflow-test
```
Or run tests locally:
```bash
pytest tests/
```

6. Access the Airflow UI at http://localhost:8080 (login: airflow / airflow)

### Secrets Management

This setup utilizes a pattern for managing secrets required by specific projects (e.g., API keys for `market-analysis`).

1.  **`.env` Files:** Store sensitive credentials in a `.env` file within the *source project's* repository (e.g., `../market-analysis/.env`). **Do not commit `.env` files to Git.**
2.  **`docker-compose.yml`:** Modify the `docker-compose.yml` file in `airflow-hub`:
    *   Use the `env_file` directive in relevant Airflow services (`airflow-webserver`, `airflow-scheduler`, `airflow-worker`, `airflow-init`) to load the external `.env` file.
    *   Define environment variables within the `environment:` block for these services to create Airflow Variables. Use the format `AIRFLOW_VAR_<VARIABLE_NAME>: ${DOTENV_VARIABLE_NAME:-}`.
        *Example:* `AIRFLOW_VAR_BINANCE_API_KEY: ${BINANCE_API_KEY:-}`
3.  **DAG Usage:** Access these secrets within DAGs using Airflow Variables, typically via Jinja templating in operators: `{{ var.value.variable_name }}`.
    *Example:* `api_key = '{{ var.value.binance_api_key }}'`

This approach keeps secrets out of the Airflow metadata database and repository code, sourcing them directly from the relevant project at runtime.

## Project Management

### Adding a New Project

1. Create project directories:
   ```
   mkdir -p dags/project_new
   mkdir -p plugins/project_new
   mkdir -p tests/dags/project_new
   mkdir -p tests/plugins/project_new
   ```

2. Define project-specific connections in Airflow UI with proper namespacing:
   - `project_new_db`
   - `project_new_api`

3. Create project-specific resource pool:
   - Pool name: `project_new_pool`
   - Slots: Based on project requirements

### Project Isolation

- Each project has its own namespace for connections, variables, and pools
- DAG IDs are prefixed with project name: `project_new_*`
- Resource allocation is managed through Airflow pools

## Contributing

Please refer to the development guidelines in `docs/dev/CONTRIBUTING.md`.

## License

This project is the private property of M. Preston Sparks. All rights reserved.
