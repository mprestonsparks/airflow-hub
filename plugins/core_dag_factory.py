# plugins/core_dag_factory.py
import re
import logging
import traceback
from pathlib import Path
import yaml
import pendulum
from datetime import timedelta
from airflow.utils.dates import cron_presets
from airflow.utils.module_loading import import_string
from airflow.exceptions import AirflowException
from airflow.models.dag import DAG

log = logging.getLogger(__name__)

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

def validate_dag_filename(filename):
    match = FILENAME_RE.fullmatch(filename)
    if not match:
        return None
    parts = match.groupdict()
    provider = parts.get('provider', '').lower()
    asset_match = parts.get('asset')
    asset = asset_match.lower() if asset_match else '' # Handle None before lower(), default to empty string
    file_domain = parts.get('domain', '').lower()

    # Validate Provider
    if provider not in VALID_PROVIDERS:
        log.error(f"INVALID PROVIDER in filename '{filename}': Provider '{provider}' is not in the approved list {VALID_PROVIDERS}. Skipping.")
        return None

    # Validate Asset (only if present)
    if asset and asset not in VALID_ASSETS:
        log.error(f"INVALID ASSET in filename '{filename}': Asset '{asset}' is not in the approved list {VALID_ASSETS}. Skipping.")
        return None

    # Validate Domain matches folder
    if file_domain not in ['ingestion', 'execution', 'transformation', 'analytics']:
        log.error(f"DOMAIN MISMATCH in filename '{filename}': Domain part '{file_domain}' does not match parent folder. Skipping.")
        return None

    return provider, asset, file_domain, filename.split('.')[0]

def timedelta_from_config(value):
    """Converts an integer (seconds) or string ('HH:MM:SS') to timedelta."""
    if isinstance(value, int):
        return timedelta(seconds=value)
    elif isinstance(value, str):
        try:
            parts = list(map(int, value.split(':')))
            if len(parts) == 3:
                return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
            elif len(parts) == 2:
                return timedelta(minutes=parts[0], seconds=parts[1])
            elif len(parts) == 1:
                return timedelta(seconds=parts[0])
        except ValueError:
            log.warning(f"Could not parse timedelta string: {value}")
    elif value is not None: # Log if it's not None but also not int/str
        log.warning(f"Unsupported type for timedelta conversion: {type(value)}")
    return None # Return None if conversion fails or input is None

def generate_yaml_dags(dag_root=None):
    """Scans YAML files in subdirectories and generates Airflow DAGs.

    Args:
        dag_root (str or Path, optional): The root directory containing DAG domain subfolders.
                                   Defaults to the 'dags' directory relative to this script.

    Returns:
        dict: A dictionary mapping generated dag_id (str) to DAG objects.
    """
    log.info("--- Starting generate_yaml_dags --- ") # Added log
    generated_dags = {}
    if dag_root is None:
        # Default to the directory containing this script if not provided
        dag_root = Path(__file__).parent.parent / 'dags' # Navigate up from plugins to the repo root
    elif isinstance(dag_root, str):
        # Convert to Path object if provided as a string
        dag_root = Path(dag_root)

    log.info(f"Calculated DAG_ROOT path: {dag_root} (Type: {type(dag_root)})")

    log.info(f"Inside generate_yaml_dags, received dag_root: '{dag_root}' (Type: {type(dag_root)})")
    if not isinstance(dag_root, Path):
        log.error(f"dag_root is NOT a Path object! Type is {type(dag_root)}. This will likely cause errors.")
        # Optionally, you could raise an error here or try to convert
        # For now, let's log and see if it proceeds.

    if not dag_root.is_dir():
        log.error(f"DAG root directory '{dag_root}' not found or is not a directory.")
        return generated_dags

    # Define domain subdirectories to scan (adjust as needed)
    # TODO: Consider making this configurable?
    domain_dirs = ['ingestion', 'execution', 'transformation', 'analytics'] 
    scan_paths = [dag_root / domain for domain in domain_dirs]

    log.info(f"Scanning for DAG definition files in: {scan_paths}")

    for scan_path in scan_paths:
        if not scan_path.is_dir():
            log.warning(f"Scan path '{scan_path}' not found, skipping.")
            continue

        search_pattern = scan_path / "*.yaml"
        log.info(f"Using search pattern: '{search_pattern}' (Type: {type(search_pattern)})") # Added type log
        try:
            log.info("Attempting glob operation...")
            yaml_files = list(search_pattern.glob('*.yaml'))
            log.info(f"Glob operation successful. Found {len(yaml_files)} potential YAML files: {yaml_files}")
        except Exception as e:
            log.exception(f"Error during glob operation with pattern '{search_pattern}': {e}")
            return generated_dags # Stop processing if glob fails

        if not yaml_files:
            log.warning(f"No YAML files found matching the pattern in subdirectories of {dag_root}.")
            return generated_dags

        for yaml_path in yaml_files:
            log.debug(f"Processing file: {yaml_path}")

            # --- Filename Validation & DAG ID Derivation ---
            validation_result = validate_dag_filename(yaml_path.name)
            if not validation_result:
                log.warning(f"Skipping invalid filename: {yaml_path.name}")
                continue

            provider, asset, domain, expected_dag_id = validation_result
            log.info(f"Validation passed for '{yaml_path.name}'. Attempting native DAG generation...")
            log.info(f"Generating DAG from: {yaml_path} with expected ID: {expected_dag_id}")

            # --- YAML Loading ---
            try:
                with open(yaml_path, 'r') as f:
                    cfg = yaml.safe_load(f)
            except yaml.YAMLError as e:
                log.error(f"Error parsing YAML file {yaml_path}: {e}")
                continue
            except Exception as e:
                log.error(f"Error reading file {yaml_path}: {e}")
                continue

            if not isinstance(cfg, dict) or expected_dag_id not in cfg:
                log.error(f"Invalid YAML structure or missing top-level key '{expected_dag_id}' in {yaml_path}")
                continue

            # --- DAG Configuration Parsing ---
            dag_config = cfg.get(expected_dag_id, {}).get('dag', {})
            default_args_config = cfg.get('default', {})

            dag_kwargs = {
                'description': dag_config.get('description'),
                'schedule': dag_config.get('schedule_interval', dag_config.get('schedule')), # Support both
                # 'start_date': handled below,
                'catchup': dag_config.get('catchup', False),
                'tags': dag_config.get('tags', []), # Ensure tags is a list
                'default_args': default_args_config.copy(), # Use a copy
                'params': dag_config.get('params', {}), # Add params support
                'max_active_runs': dag_config.get('max_active_runs', 16), # Default from Airflow
                'max_active_tasks': dag_config.get('max_active_tasks', 16), # Default from Airflow
                'dagrun_timeout': timedelta_from_config(dag_config.get('dagrun_timeout')), # Use helper
                # Add other DAG parameters as needed: on_success_callback, etc.
            }

            # Add owner from default_args if not overridden in DAG config
            if 'owner' not in dag_kwargs['default_args'] and 'owner' in default_args_config:
                dag_kwargs['default_args']['owner'] = default_args_config['owner']
            # Clean up retry_delay format (remove _sec suffix if present)
            if 'retry_delay_sec' in dag_kwargs['default_args']:
                delay_val = dag_kwargs['default_args'].pop('retry_delay_sec')
                dag_kwargs['default_args']['retry_delay'] = timedelta(seconds=int(delay_val))
            elif 'retry_delay' in dag_kwargs['default_args']:
                # Ensure retry_delay is timedelta if specified directly
                dag_kwargs['default_args']['retry_delay'] = timedelta_from_config(dag_kwargs['default_args']['retry_delay'])

            # Parse schedule if it's a cron preset name
            if isinstance(dag_kwargs['schedule'], str) and dag_kwargs['schedule'] in cron_presets:
                dag_kwargs['schedule'] = cron_presets[dag_kwargs['schedule']]

            # --- start_date Processing ---
            start_date_value = dag_config.get('start_date')
            parsed_start_date = None
            is_jinja_template = False
            jinja_start_date_str = None

            if isinstance(start_date_value, str):
                if '{{' in start_date_value and '}}' in start_date_value:
                    log.debug(f"DAG {expected_dag_id}: Identified Jinja template start_date string: '{start_date_value}'. Will assign post-initialization.")
                    is_jinja_template = True
                    jinja_start_date_str = start_date_value
                else:
                    try:
                        parsed_start_date = pendulum.parse(start_date_value)
                        log.debug(f"DAG {expected_dag_id}: Parsed static start_date string: {parsed_start_date}")
                    except Exception as e:
                        log.warning(f"DAG {expected_dag_id}: Could not parse start_date string '{start_date_value}': {e}")
            elif isinstance(start_date_value, dict) and 'days' in start_date_value:
                try:
                    days_ago = int(start_date_value['days'])
                    parsed_start_date = pendulum.today('UTC').add(days=-days_ago)
                    log.debug(f"DAG {expected_dag_id}: Calculated relative start_date ({days_ago} days ago): {parsed_start_date}")
                except (ValueError, TypeError) as e:
                    log.error(f"DAG {expected_dag_id}: Invalid relative start_date value in {yaml_path}: {start_date_value} - {e}")
            elif start_date_value is not None:
                log.warning(f"DAG {expected_dag_id}: Unsupported start_date type '{type(start_date_value)}' in {yaml_path}: {start_date_value}")

            # Only add start_date to kwargs if it was successfully parsed/calculated (NOT Jinja)
            if parsed_start_date is not None and not is_jinja_template:
                dag_kwargs['start_date'] = parsed_start_date
            else:
                if start_date_value is not None and not is_jinja_template:
                    log.warning(f"DAG {expected_dag_id}: start_date '{start_date_value}' could not be parsed or is invalid. Check DAG configuration in {yaml_path}.")

            # Filter out None values from dag_kwargs
            dag_kwargs = {k: v for k, v in dag_kwargs.items() if v is not None}

            # --- DAG Initialization ---
            log.debug(f"DAG {expected_dag_id}: Initializing with kwargs: {dag_kwargs}")
            try:
                dag = DAG(
                    dag_id=expected_dag_id,
                    **dag_kwargs
                )
            except Exception as e:
                log.error(f"DAG {expected_dag_id}: Failed during DAG() initialization with kwargs {dag_kwargs}: {e}")
                log.debug(traceback.format_exc())
                continue

            # Assign Jinja start_date AFTER DAG creation if needed
            if is_jinja_template and jinja_start_date_str:
                log.debug(f"DAG {expected_dag_id}: Assigning Jinja template string '{jinja_start_date_str}' to dag.start_date post-initialization.")
                dag.start_date = jinja_start_date_str
            elif not hasattr(dag, 'start_date') or dag.start_date is None:
                log.error(f"DAG {expected_dag_id}: Critical error - DAG object lacks a start_date after initialization. Check config '{yaml_path}'.")
                continue

            # --- Task Creation Loop ---
            tasks_config = cfg.get(expected_dag_id, {}).get('tasks', {})
            tasks = {}
            task_dependencies = {}

            with dag:
                for task_id, task_config in tasks_config.items():
                    operator_path = task_config.get('operator')
                    if not operator_path:
                        log.error(f"Task {task_id} in DAG {expected_dag_id} is missing 'operator' definition.")
                        continue

                    try:
                        OperatorClass = import_string(operator_path)
                    except ImportError as e:
                        log.error(f"Could not import operator '{operator_path}' for task {task_id} in DAG {expected_dag_id}: {e}")
                        continue

                    # Prepare operator arguments, removing non-init args
                    op_kwargs = task_config.copy()
                    op_kwargs.pop('operator', None)
                    dependencies = op_kwargs.pop('dependencies', [])
                    task_dependencies[task_id] = dependencies # Store for later linking

                    # Convert execution_timeout to timedelta if present
                    if 'execution_timeout' in op_kwargs:
                        op_kwargs['execution_timeout'] = timedelta_from_config(op_kwargs['execution_timeout'])

                    # Instantiate operator
                    try:
                        # No need to explicitly pass dag=dag here due to 'with dag:' context
                        tasks[task_id] = OperatorClass(task_id=task_id, **op_kwargs)
                        log.debug(f"Created task '{task_id}' of type {operator_path} for DAG {expected_dag_id}")
                    except Exception as e:
                        log.error(f"Failed to create task {task_id} in DAG {expected_dag_id}: {e}")
                        log.debug(traceback.format_exc())
                        # Decide whether to skip DAG or just task
                        continue # Skip this task

                # --- Set Task Dependencies ---
                for task_id, dependencies in task_dependencies.items():
                    if task_id not in tasks:
                        continue # Task creation failed
                    upstream_tasks = []
                    for dep_id in dependencies:
                        if dep_id in tasks:
                            upstream_tasks.append(tasks[dep_id])
                        else:
                            log.warning(f"Dependency '{dep_id}' not found for task '{task_id}' in DAG '{expected_dag_id}'.")

                    if upstream_tasks:
                        tasks[task_id].set_upstream(upstream_tasks)
                        log.debug(f"Set dependencies for task '{task_id}': {dependencies}")

            # Store the successfully generated DAG
            if expected_dag_id not in generated_dags: # Avoid overwriting if duplicate filenames exist
                generated_dags[expected_dag_id] = dag
                log.info(f"Successfully generated DAG '{expected_dag_id}' using native Python.")
            else:
                log.warning(f"Duplicate DAG ID '{expected_dag_id}' detected. Keeping the first one generated.")

    log.info(f"--- Finished generate_yaml_dags. Generated {len(generated_dags)} DAGs. ---") # Added log
    return generated_dags
