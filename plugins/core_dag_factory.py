# plugins/core_dag_factory.py
import re
import logging
from pathlib import Path
import yaml
import pendulum
from datetime import timedelta

from airflow.models.dag import DAG
from airflow.utils.module_loading import import_string

log = logging.getLogger(__name__)

DAG_ROOT = Path(__file__).parent.parent / "dags"
log.info(f"Calculated DAG_ROOT path: {DAG_ROOT.resolve()}")

DOMAIN_DIRS = ("ingestion", "execution", "transformation", "analytics")

# Regex based on DAG_RESTRUCTURE_PLAN.md § 1: {provider}_{optional-asset}_{domain}.py
# Adjusted for YAML and allowing provider/asset to be more general alphanumeric
# Ensures domain part matches one of the approved folders strictly.
FILENAME_RE = re.compile(r"^(?P<provider>[a-z0-9]+)(?:_(?P<asset>[a-z0-9]+))?_(?P<domain>ingestion|execution|transformation|analytics)\.ya?ml$", re.IGNORECASE)

# Controlled Vocabularies from (2025-04-23) DAG_RESTRUCTURE_PLAN.md § 3 & 4
# Lowercased for case-insensitive matching
VALID_PROVIDERS = {
    "ibkr", "binance", "coinbase", "alpaca", "kraken",
    "tradestation", "tdameritrade", "gemini"
}
VALID_ASSETS = {
    "equities", "spot", "futures", "options", "forex", "bonds"
}

# Scan for YAML files, validate them, and generate DAGs into the global namespace
log.info(f"Scanning for DAG definition files in: {[str(DAG_ROOT / domain) for domain in DOMAIN_DIRS]}")
yaml_files_found = 0

for domain in DOMAIN_DIRS:
    domain_path = DAG_ROOT / domain
    if not domain_path.is_dir():
        log.warning(f"Domain directory not found, skipping: {domain_path}")
        continue

    for cfg_path in domain_path.glob("*.y*ml"):
        log.debug(f"Found potential DAG definition file: {cfg_path}")
        yaml_files_found += 1
        match = FILENAME_RE.fullmatch(cfg_path.name)

        if not match:
            log.error(f"INVALID FILENAME: '{cfg_path.name}' does not match the required ontology pattern {{provider}}_[{{asset}}]_{{domain}}.yaml. Skipping.")
            continue

        parts = match.groupdict()
        provider = parts.get('provider', '').lower()
        asset_match = parts.get('asset')
        asset = asset_match.lower() if asset_match else '' # Handle None before lower(), default to empty string
        file_domain = parts.get('domain', '').lower()

        # Validate Provider
        if provider not in VALID_PROVIDERS:
            log.error(f"INVALID PROVIDER in filename '{cfg_path.name}': Provider '{provider}' is not in the approved list {VALID_PROVIDERS}. Skipping.")
            continue

        # Validate Asset (only if present)
        if asset and asset not in VALID_ASSETS:
            log.error(f"INVALID ASSET in filename '{cfg_path.name}': Asset '{asset}' is not in the approved list {VALID_ASSETS}. Skipping.")
            continue

        # Validate Domain matches folder
        if file_domain != domain.lower():
             log.error(f"DOMAIN MISMATCH in filename '{cfg_path.name}': Domain part '{file_domain}' does not match parent folder '{domain}'. Skipping.")
             continue

        # --- Validation Passed --- 
        log.info(f"Validation passed for '{cfg_path.name}'. Attempting native DAG generation...")
        expected_dag_id = cfg_path.stem # Filename without extension
        try:
            log.info(f"Generating DAG from: {cfg_path} with expected ID: {expected_dag_id}")
            
            # Load YAML config
            with open(cfg_path, 'r') as f:
                config = yaml.safe_load(f)
            
            if not isinstance(config, dict):
                 log.error(f"Invalid YAML structure in {cfg_path}: Expected a dictionary at the top level. Skipping.")
                 continue

            # Extract configurations
            dag_specific_config = config.get(expected_dag_id, {})
            dag_config = dag_specific_config.get('dag', {})
            tasks_config = dag_specific_config.get('tasks', {})
            default_config = config.get('default', {})

            if not dag_config or not tasks_config:
                log.error(f"Invalid YAML structure in {cfg_path}: Missing 'dag' or 'tasks' section under '{expected_dag_id}'. Skipping.")
                continue

            # Prepare default_args
            default_args = default_config.copy()
            if 'retry_delay_sec' in default_args:
                default_args['retry_delay'] = timedelta(seconds=default_args.pop('retry_delay_sec'))
            
            # Prepare DAG kwargs
            dag_kwargs = {
                'description': dag_config.get('description'),
                'schedule': dag_config.get('schedule_interval'), # Use 'schedule' for DAG constructor
                'start_date': dag_config.get('start_date'), # Pass string directly, Airflow handles Jinja
                'tags': dag_config.get('tags'),
                'params': dag_config.get('params'),
                'catchup': dag_config.get('catchup', default_config.get('catchup', False)), # Default catchup to False
                'default_args': default_args,
            }
            # Filter out None values from dag_kwargs
            dag_kwargs = {k: v for k, v in dag_kwargs.items() if v is not None}

            # Create DAG
            dag = DAG(
                dag_id=expected_dag_id,
                **dag_kwargs
            )

            # Create Tasks
            tasks = {}
            with dag: # Use DAG as context manager
                for task_id, task_config in tasks_config.items():
                    operator_path = task_config.get('operator')
                    if not operator_path:
                        log.error(f"Missing 'operator' for task '{task_id}' in {cfg_path}. Skipping task.")
                        continue
                    
                    try:
                        OperatorClass = import_string(operator_path)
                    except ImportError:
                        log.error(f"Could not import operator '{operator_path}' for task '{task_id}' in {cfg_path}. Skipping task.", exc_info=True)
                        continue
                        
                    # Prepare operator arguments
                    op_kwargs = task_config.copy()
                    op_kwargs.pop('operator', None)
                    op_kwargs.pop('depends_on', None) # Remove potential old dependency key
                    op_kwargs.pop('upstream', None) # Remove potential old dependency key
                    op_kwargs.pop('downstream', None) # Remove potential old dependency key

                    # Instantiate operator
                    tasks[task_id] = OperatorClass(task_id=task_id, **op_kwargs)

            # TODO: Implement task dependencies based on YAML config (e.g., using 'upstream'/'downstream' keys)

            # Register DAG
            globals()[expected_dag_id] = dag
            log.info(f"Successfully generated DAG '{expected_dag_id}' using native Python.")

        except Exception as e:
            log.error(f"Failed to generate DAG from {cfg_path}: {e}", exc_info=True)

if yaml_files_found == 0:
    log.warning("No YAML DAG definition files found in any domain directory.")
