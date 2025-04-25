# dags/dag_factory_runner.py
"""
This file acts as a trigger for the DAG factory located in the plugins folder.

When the DagBag scans the DAGs folder, it will execute this file.
Importing the core_dag_factory module here causes its logic to run,
which scans the domain-specific subdirectories for YAML definitions
and generates the corresponding DAG objects.
"""

# ADDED: Import DAG to satisfy safe discovery mode
from airflow.models.dag import DAG

import logging

log = logging.getLogger(__name__)

print("DEBUG: dag_factory_runner.py execution START.")

try:
    print("DEBUG: Attempting to import core_dag_factory...")
    # Attempt to import the factory script from the plugins directory.
    # This assumes 'plugins' is effectively on the Python path for Airflow.
    from plugins import core_dag_factory
    print("DEBUG: Import of core_dag_factory SUCCEEDED.")
    log.info("Successfully imported and executed core_dag_factory from plugins.")
except ImportError as e:
    print(f"DEBUG: Import of core_dag_factory FAILED: {e}")
    log.error(f"Failed to import core_dag_factory from plugins: {e}", exc_info=True)
    log.error("DAG generation from YAML files will not occur.")
except Exception as e:
    print(f"DEBUG: An unexpected error occurred: {e}")
    # Catch any other unexpected errors during the factory execution
    # Log more details about the exception
    log.error(f"An unexpected error occurred during the execution of core_dag_factory: {e}", exc_info=True)
    # Commented out potentially noisy log message
    # log.error("DAG generation may be incomplete.")

print("DEBUG: dag_factory_runner.py execution END.")

# No DAG object is explicitly defined here; the factory handles generation.
