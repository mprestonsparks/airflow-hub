# dags/yaml_dag_loader.py
import os
import sys
import logging
from pathlib import Path

# --- Add plugins directory to Python path ---
# Calculate the absolute path to the directory containing this script
_DAGS_DIR = Path(__file__).parent
_PLUGINS_DIR = _DAGS_DIR.parent / 'plugins'
# Add the plugins directory to sys.path if it's not already there
if str(_PLUGINS_DIR) not in sys.path:
    sys.path.append(str(_PLUGINS_DIR))
# --- End path modification ---

log = logging.getLogger(__name__)

log.info("--- Running yaml_dag_loader.py ---")
log.info(f"DEBUG: sys.path includes: {sys.path}") # Log sys.path for verification

# Determine the DAG root directory within the container
# Default to /opt/airflow/dags if AIRFLOW_HOME isn't set explicitly for path resolution
dag_root_in_container = os.environ.get("AIRFLOW_HOME", "/opt/airflow/dags")
log.info(f"DEBUG: DAG root in container: {dag_root_in_container}")

try:
    # Call the factory function to get the generated DAGs
    # Pass the expected root path inside the container
    log.info("DEBUG: Attempting to locate DAG factory...")
    dag_factory_path = os.path.join(dag_root_in_container, '..', 'plugins', 'core_dag_factory.py')
    log.info(f"DEBUG: Expected DAG factory path: {dag_factory_path}")
    log.info("DEBUG: Attempting to import generate_yaml_dags from core_dag_factory")
    from core_dag_factory import generate_yaml_dags
    log.info("DEBUG: Successfully imported generate_yaml_dags.")

    log.info(f"DEBUG: Calling generate_yaml_dags with dag_root: {dag_root_in_container}")
    generated_dags = generate_yaml_dags(dag_root=dag_root_in_container)

    log.info(f"DEBUG: Factory returned {len(generated_dags)} DAGs. Registering them...")

    if generated_dags:
        log.info(f"DEBUG: Generated {len(generated_dags)} DAGs. Registering them...")
        # Dynamically add the generated DAGs to the global namespace
        globals().update(generated_dags)
        log.info("DEBUG: DAGs registered in globals().")
        # Log the registered DAG IDs for confirmation
        for dag_id, dag_object in generated_dags.items():
            log.info(f"DEBUG: Registered DAG: {dag_id}")
    else:
        log.warning("DEBUG: generate_yaml_dags returned no DAGs.")

except NameError as e:
    # Handle case where generate_yaml_dags couldn't be imported
    log.error(f"ERROR: DAG generation function not found: {e}")
except ImportError as e:
    log.error(f"ERROR: Failed to import generate_yaml_dags: {e}", exc_info=True)
    log.error("ERROR: Ensure core_dag_factory.py is in the Airflow plugins folder and accessible.")
except Exception as e:
    log.error(f"ERROR: An error occurred during DAG generation: {e}", exc_info=True)

log.info("--- Finished yaml_dag_loader.py ---")
