# plugins/core_dag_factory.py
import re
import logging
from pathlib import Path

try:
    import dagfactory
except ImportError:
    logging.error("dag-factory not installed. Please install it: pip install dag-factory")
    dagfactory = None # Avoid crashing scheduler if not installed, log error instead

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

if dagfactory:
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
            asset = parts.get('asset', '').lower() # Will be '' if not present
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
            log.info(f"Validation passed for '{cfg_path.name}'. Attempting DAG generation...")
            try:
                expected_dag_id = cfg_path.stem # Filename without extension
                log.info(f"Generating DAG from: {cfg_path} with expected ID: {expected_dag_id}")
                # dag-factory expects the config path as a string
                factory = dagfactory.DagFactory(str(cfg_path))
                
                # Set the dag_id explicitly to match the filename stem, overriding any value in the YAML
                factory.build(dag_id=expected_dag_id)
                
                # Generate DAGs into the global namespace
                factory.generate_dags(globals())
                log.info(f"Successfully generated DAG '{expected_dag_id}'")

            except Exception as e:
                log.error(f"Failed to generate DAG from {cfg_path}: {e}", exc_info=True)

    if yaml_files_found == 0:
        log.warning("No YAML DAG definition files found in any domain directory.")
else:
    log.error("dag-factory library not found. DAG generation skipped.")
