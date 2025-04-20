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
│   ├── Dockerfile.airflow # Main Airflow image
│   └── project_specific/  # Project-specific Docker images
│
├── requirements.txt       # Core dependencies
└── .airflowignore        # Patterns to exclude from DAG parsing
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

3. Initialize the Airflow database and create admin user:
   ```bash
   docker-compose run --rm airflow-init
   ```

4. Start Airflow services:
   ```bash
   docker-compose up -d
   ```

5. Verify DAGs and tests:
   ```bash
   docker-compose exec airflow-webserver airflow dags list
   docker-compose exec airflow-webserver airflow dags list-import-errors
   pytest tests/test_dag_validation.py
   ```

6. Access the Airflow UI at http://localhost:8080 (login: airflow / airflow)

For advanced use or CLI development, see detailed docs in docs/INTEGRATION_QUICKSTART.md.

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

1. Follow the project structure and naming conventions
2. Keep project boundaries clear - no cross-project imports
3. Move shared functionality to common modules
4. Add tests for all new code
5. Document connections and external dependencies

## License
Property of
(c) M. Preston Sparks, 2025 
All rights reserved. 
