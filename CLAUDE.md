# CLAUDE.md - Airflow Hub Repository

This file provides repository-specific guidance for the Airflow Hub system.

## Review Report Requirements

<review-report-standards>
When creating review reports for completed tasks, Claude Code MUST follow these standards:

1. **Naming Convention**: 
   - XML format: `REVIEW_REPORT_YYYY-MM-DD-HHMM_XML.md`
   - Markdown format: `REVIEW_REPORT_YYYY-MM-DD-HHMM_MD.md`
   - Example: `REVIEW_REPORT_2025-06-27-1452_XML.md` and `REVIEW_REPORT_2025-06-27-1452_MD.md`
   - Time should be in 24-hour format (e.g., 1452 for 2:52 PM)

2. **Dual Format Requirement**:
   - Always create TWO versions of each review report
   - XML version: Use XML syntax throughout for structured data
   - Markdown version: Use standard markdown formatting for readability
   - Both must contain identical information, only formatting differs

3. **Storage Location**:
   - All review reports MUST be saved in: `.claude/review-reports/`
   - Create the directory if it doesn't exist: `mkdir -p .claude/review-reports`
   - This applies to ALL repositories in the DEAN system

4. **Required Metadata**:
   Each review report MUST include metadata at the top:
   ```xml
   <report-metadata>
     <creation-date>YYYY-MM-DD</creation-date>
     <creation-time>HH:MM PST/EST</creation-time>
     <report-type>Implementation Review/Bug Fix/Feature Addition/etc.</report-type>
     <author>Claude Code Assistant</author>
     <system>DEAN</system>
     <component>Component Name</component>
     <task-id>Unique Task Identifier</task-id>
   </report-metadata>
   ```
</review-report-standards>

## Repository Context

Airflow Hub provides the workflow orchestration layer for the DEAN (Distributed Evolutionary Agent Network) system. This repository contains DAG definitions, custom operators, and scheduling logic that coordinate agent evolution cycles, pattern discovery, and system maintenance tasks.

## CRITICAL: This is Part of a Distributed System

<distributed_system_warning>
⚠️ **WARNING: The DEAN system spans FOUR repositories** ⚠️

This repository contains ONLY the workflow orchestration components. Other components are located in:
- **DEAN**: Orchestration, authentication, monitoring (Port 8082-8083)
- **IndexAgent**: Agent logic, evolution algorithms (Port 8081)
- **infra**: Docker configs, database schemas, deployment scripts

**Specification Documents Location**: DEAN/specifications/ (read-only)

Always check all repositories before implementing features!
</distributed_system_warning>

## Critical Implementation Requirements

### NO MOCK IMPLEMENTATIONS

<implementation_standards>
When implementing any feature in this codebase, Claude Code MUST create actual, working code. The following are STRICTLY PROHIBITED:
- Mock implementations or stub functions presented as complete
- Placeholder code with TODO comments in "finished" work
- Simulated test results or hypothetical outputs
- Documentation of what "would" happen instead of what "does" happen
- Pseudocode or conceptual implementations claimed as functional

Every implementation MUST:
- Be fully functional and executable with proper error handling
- Work with actual services and dependencies
- Be tested with real commands showing actual output
- Include complete implementations of all code paths
</implementation_standards>

## Airflow Hub-Specific Architecture

### Core Responsibilities
- **Evolution Orchestration**: Scheduling and monitoring agent evolution cycles
- **Economic Governance**: Enforcing token budget constraints via DAGs
- **Pattern Discovery**: Automated pattern detection and propagation workflows
- **System Maintenance**: Resource cleanup, monitoring, and optimization tasks
- **Task Coordination**: Managing parallel agent execution and dependencies

### Key Components in This Repository

```
dags/
├── dean/                          # All DEAN-related DAGs
│   ├── dean_agent_evolution.py    # Main evolution orchestration
│   ├── dean_evolution_cycle.py    # Complete evolution cycle
│   ├── dean_system_maintenance.py # System maintenance tasks
│   ├── dean_population_manager.py # Population management
│   ├── dean_token_economy.py      # Economic governance
│   ├── dean_pattern_discovery.py  # Pattern detection
│   ├── dean_test_integration.py   # Integration testing
│   ├── dean_contracts.py          # Data contracts
│   ├── config.yaml               # DEAN configuration
│   └── utils/                    # Utility clients
│       ├── economic_client.py    # Economic API client
│       ├── claude_api_client.py  # Claude integration
│       └── diversity_client.py   # Diversity management

plugins/
└── agent_evolution/              # Custom operators
    ├── operators/
    │   ├── agent_evolution_operator.py  # Evolution trigger
    │   └── agent_spawn_operator.py      # Agent spawning
    └── hooks/
        └── dean_api_hook.py      # DEAN API integration
```

### What This Repository Does NOT Contain
- **Agent Implementation**: Located in IndexAgent/indexagent/agents/
- **API Services**: Located in DEAN/src/dean_orchestration/
- **Docker Configurations**: Located in infra/docker-compose.dean.yml
- **Database Schemas**: Located in infra/database/

## Development Standards

### DAG Development Requirements

<dag_rules>
<rule context="error_handling">
All DAGs must implement comprehensive error handling with retry logic and failure callbacks.
</rule>

<rule context="task_dependencies">
Define explicit task dependencies to prevent race conditions. Use trigger rules appropriately.
</rule>

<rule context="economic_constraints">
Every evolution-related task must check token budgets before execution.
</rule>

<rule context="monitoring">
Include task-level metrics and logging for observability.
</rule>
</dag_rules>

### DAG Implementation Pattern

```python
# REQUIRED: Complete DAG implementation with error handling
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'dean-system',
    'depends_on_past': False,
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'dean_evolution_cycle',
    default_args=default_args,
    description='Complete agent evolution cycle with budget enforcement',
    schedule_interval='@daily',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['dean', 'evolution'],
) as dag:
    
    def check_budget(**context):
        """Check available token budget"""
        try:
            response = economic_client.get_available_budget()
            if response['available'] < MIN_BUDGET:
                raise ValueError(f"Insufficient budget: {response['available']}")
            return response['available']
        except Exception as e:
            logger.error(f"Budget check failed: {e}")
            raise
    
    budget_check = PythonOperator(
        task_id='check_budget',
        python_callable=check_budget,
        on_failure_callback=alert_on_failure,
    )
```

## Configuration

### DEAN DAG Configuration
```yaml
# dags/dean/config.yaml
dean:
  connections:
    dean_api: "dean-orchestration"
    indexagent_api: "indexagent"
    evolution_api: "evolution-api"
  
  variables:
    default_token_budget: 10000
    max_population_size: 50
    evolution_generations: 20
  
  dependencies:
    - dean-api-hook
    - agent-evolution-operators
```

## Service Integration

### API Endpoints
- **DEAN Orchestrator**: http://dean-orchestration:8082
- **IndexAgent**: http://indexagent:8081
- **Evolution API**: http://evolution-api:8090
- **Economic Governor**: http://infra-api:8091

### Airflow Connections
Configure these in Airflow UI or via CLI:
```bash
airflow connections add dean_api \
    --conn-type http \
    --conn-host dean-orchestration \
    --conn-port 8082

airflow connections add indexagent_api \
    --conn-type http \
    --conn-host indexagent \
    --conn-port 8081
```

## Common Commands

```bash
# Development
airflow standalone                    # Start Airflow in standalone mode
airflow dags list                    # List all DAGs
airflow tasks test dean_evolution_cycle check_budget 2024-01-01  # Test task

# DAG Management
airflow dags trigger dean_evolution_cycle  # Manually trigger DAG
airflow dags pause dean_system_maintenance # Pause DAG
airflow dags backfill dean_pattern_discovery --start-date 2024-01-01  # Backfill

# Monitoring
airflow tasks states-for-dag-run dean_evolution_cycle run_2024_01_01  # Check task states
airflow dags show dean_evolution_cycle  # Visualize DAG
```

## Testing Requirements

<testing_standards>
- Unit tests for all custom operators and hooks
- Integration tests for complete DAG runs
- Mock external service calls in tests
- Validate task dependencies and trigger rules
- Test error handling and retry logic
- Performance tests for large-scale operations
</testing_standards>

### Test Pattern
```python
# tests/test_dean_evolution_dag.py
import pytest
from airflow.models import DagBag

def test_dean_evolution_dag_loaded():
    """Test that DAG loads without errors"""
    dagbag = DagBag(include_examples=False)
    dag = dagbag.get_dag('dean_evolution_cycle')
    assert dag is not None
    assert len(dag.tasks) > 0

def test_task_dependencies():
    """Test task dependency chain"""
    dagbag = DagBag(include_examples=False)
    dag = dagbag.get_dag('dean_evolution_cycle')
    
    budget_task = dag.get_task('check_budget')
    spawn_task = dag.get_task('spawn_agents')
    
    assert spawn_task in budget_task.downstream_list
```

## Security Requirements

<security_rules>
- Store sensitive credentials in Airflow Connections/Variables
- Never hardcode API keys or passwords in DAGs
- Implement access controls for DAG modifications
- Audit log all evolution triggers
- Validate all external inputs
</security_rules>