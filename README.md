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

### Prerequisites

- Python 3.8+
- Docker and Docker Compose (for containerized approach)
- Access to required external systems (databases, APIs, etc.)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-org/airflow-hub.git
   cd airflow-hub
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up Airflow:
   ```
   export AIRFLOW_HOME=$(pwd)
   airflow db init
   airflow users create --username admin --password admin --firstname Admin --lastname User --role Admin --email admin@example.com
   ```

4. Start Airflow services:
   ```
   airflow webserver -p 8080
   airflow scheduler
   ```

### Docker Deployment

For containerized deployment:

```
docker-compose up -d
```

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
