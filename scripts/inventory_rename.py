# scripts/inventory_rename.py
import ast
import logging
import re
from pathlib import Path
import sys

# Add project root to path to allow importing migration.overrides
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
log = logging.getLogger(__name__)

# --- Configuration (Mirrors core_dag_factory and plan) ---
DAG_ROOT = PROJECT_ROOT / "dags"
DOMAIN_DIRS = ("ingestion", "execution", "transformation", "analytics")
# Exclude the newly created domain dirs from the search for old DAGs
EXCLUDE_DIRS = [DAG_ROOT / d for d in DOMAIN_DIRS]

VALID_PROVIDERS = {
    "ibkr", "binance", "coinbase", "alpaca", "kraken",
    "tradestation", "tdameritrade", "gemini"
}
VALID_ASSETS = {
    "equities", "spot", "futures", "options", "forex", "bonds"
}

# --- Manual Overrides --- 
try:
    from migration.overrides import MIGRATION_MANUAL_OVERRIDES
    log.info(f"Loaded {len(MIGRATION_MANUAL_OVERRIDES)} manual override(s) from migration/overrides.py")
except ImportError:
    log.warning("migration/overrides.py not found or empty. Proceeding without manual overrides.")
    MIGRATION_MANUAL_OVERRIDES = {}
except Exception as e:
    log.error(f"Error loading migration/overrides.py: {e}")
    MIGRATION_MANUAL_OVERRIDES = {}

# --- Helper Functions ---
def get_dag_id_from_py(file_path: Path) -> str | None:
    """Parses a Python file with AST to find the dag_id in DAG()."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=str(file_path))
        
        for node in ast.walk(tree):
            # Look for DAG(...) or airflow.models.DAG(...)
            if isinstance(node, ast.Call) and isinstance(node.func, (ast.Name, ast.Attribute)):
                func_name = ''
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    # Handles airflow.DAG, models.DAG, etc.
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == 'airflow':
                         func_name = node.func.attr # e.g. DAG
                    elif isinstance(node.func.value, ast.Attribute) and node.func.value.attr == 'models':
                         func_name = node.func.attr # e.g. DAG
                    elif isinstance(node.func.value, ast.Name) and node.func.value.id == 'models':
                         func_name = node.func.attr # e.g. DAG
                    else:
                         func_name = node.func.attr # Simplest case like DAG(...)

                if func_name == 'DAG':
                    # Find the dag_id keyword argument
                    for keyword in node.keywords:
                        if keyword.arg == 'dag_id' and isinstance(keyword.value, ast.Constant):
                            return keyword.value.value # Return the string value
                    # Fallback: maybe dag_id is the first positional arg?
                    if node.args and isinstance(node.args[0], ast.Constant):
                        log.debug(f"Found dag_id as positional arg in {file_path.name}")
                        return node.args[0].value
        log.warning(f"Could not find dag_id in {file_path.name}")
        return None
    except Exception as e:
        log.error(f"Error parsing {file_path}: {e}")
        return None

def infer_metadata(file_path: Path, dag_id: str | None) -> dict | None:
    """Attempts basic heuristic inference of provider/asset/domain."""
    # Simplistic example: Try to find keywords in filename or dag_id
    # This needs refinement based on actual legacy naming patterns
    text_to_search = f"{file_path.stem.lower()} {dag_id.lower() if dag_id else ''}"
    found_meta = {}
    
    # Infer Domain
    for domain in DOMAIN_DIRS:
        if domain in text_to_search:
            found_meta['domain'] = domain
            break
    if 'domain' not in found_meta:
        # Default or guess based on keywords?
        if 'ingest' in text_to_search:
             found_meta['domain'] = 'ingestion'
        elif 'exec' in text_to_search or 'trade' in text_to_search:
             found_meta['domain'] = 'execution'
        elif 'transform' in text_to_search or 'agg' in text_to_search:
             found_meta['domain'] = 'transformation'
        elif 'analytic' in text_to_search or 'report' in text_to_search:
             found_meta['domain'] = 'analytics'
        else:
            log.warning(f"Cannot infer domain for {file_path.name}")
            return None # Domain is mandatory

    # Infer Provider
    for provider in VALID_PROVIDERS:
        if provider in text_to_search:
            found_meta['provider'] = provider
            break
    if 'provider' not in found_meta:
        log.warning(f"Cannot infer provider for {file_path.name}")
        return None # Provider is mandatory
        
    # Infer Asset (Optional)
    for asset in VALID_ASSETS:
        if asset in text_to_search:
            found_meta['asset'] = asset
            break # Take the first found asset

    return found_meta

# --- Main Execution ---
proposed_mappings = []

log.info(f"Starting DAG inventory in {DAG_ROOT}, excluding {EXCLUDE_DIRS}")

py_files = [f for f in DAG_ROOT.rglob("*.py") if f.is_file() and f.name != '__init__.py' and not any(f.is_relative_to(ex) for ex in EXCLUDE_DIRS)]

log.info(f"Found {len(py_files)} potential legacy Python DAG files to process.")

for py_file in py_files:
    log.info(f"Processing: {py_file.relative_to(PROJECT_ROOT)}")
    relative_path_str = str(py_file.relative_to(PROJECT_ROOT)).replace('\\', '/') # Use forward slashes for keys
    metadata = None
    source = "Inferred"
    
    # 1. Check Overrides
    if relative_path_str in MIGRATION_MANUAL_OVERRIDES:
        metadata = MIGRATION_MANUAL_OVERRIDES[relative_path_str]
        source = "Manual Override"
        log.info(f"  Using manual override: {metadata}")
        # Basic validation of override structure
        if not all(k in metadata for k in ('provider', 'domain')):
             log.error(f"  Invalid override for {relative_path_str}: missing 'provider' or 'domain'. Skipping.")
             continue
    else:
        # 2. Attempt Heuristic Inference
        old_dag_id = get_dag_id_from_py(py_file)
        if not old_dag_id:
             log.warning(f"  Skipping {py_file.name} - could not parse dag_id.")
             continue
        
        metadata = infer_metadata(py_file, old_dag_id)
        if not metadata:
             log.warning(f"  Skipping {py_file.name} - could not infer required metadata (provider/domain). Consider adding to overrides.")
             continue
        log.info(f"  Inferred metadata: {metadata}")
        source = "Heuristic Inference"
        
    # 3. Validate Metadata & Construct Target
    provider = metadata.get('provider','').lower()
    asset_value = metadata.get('asset') # Get asset value, could be None
    asset = asset_value.lower() if isinstance(asset_value, str) else None # Convert to lower only if it's a string
    domain = metadata.get('domain','').lower()

    if not provider or provider not in VALID_PROVIDERS:
        log.error(f"  Validation Failed ({source}): Invalid or missing provider '{provider}'. Skipping {py_file.name}.")
        continue
    if not domain or domain not in DOMAIN_DIRS:
         log.error(f"  Validation Failed ({source}): Invalid or missing domain '{domain}'. Skipping {py_file.name}.")
         continue
    if asset and asset not in VALID_ASSETS:
        log.error(f"  Validation Failed ({source}): Invalid asset '{asset}'. Skipping {py_file.name}.")
        continue
        
    # Construct target filename and ID
    asset_part = f"_{asset}" if asset else ""
    target_filename = f"{provider}{asset_part}_{domain}.yaml"
    target_dag_id = f"{provider}{asset_part}_{domain}"
    target_path = DAG_ROOT / domain / target_filename
    
    # 4. Store Mapping
    old_dag_id_found = get_dag_id_from_py(py_file) or "<Parse Failed>"
    mapping_entry = {
        "old_py_path": str(py_file.relative_to(PROJECT_ROOT)),
        "old_dag_id": old_dag_id_found,
        "target_yaml_path": str(target_path.relative_to(PROJECT_ROOT)),
        "target_dag_id": target_dag_id,
        "source": source,
        "inferred_provider": provider,
        "inferred_asset": asset or None, # Use the processed asset value
        "inferred_domain": domain
    }
    proposed_mappings.append(mapping_entry)
    log.info(f"  Proposed Target -> {target_path.relative_to(PROJECT_ROOT)} (DAG ID: {target_dag_id})")

# --- Output Results ---
print("\n--- Proposed DAG Migration Mapping ---")
if not proposed_mappings:
    print("No Python DAGs found requiring migration or inference failed for all found files.")
else:
    # Simple text output, consider JSON or CSV for easier parsing if needed
    print(f"Found {len(proposed_mappings)} DAGs to migrate:")
    for i, item in enumerate(proposed_mappings):
        print(f"\n{i+1}. Old Path: {item['old_py_path']} (ID: {item['old_dag_id']})")
        print(f"   Proposed YAML: {item['target_yaml_path']} (ID: {item['target_dag_id']})")
        print(f"   Ontology: provider='{item['inferred_provider']}', asset='{item['inferred_asset']}', domain='{item['inferred_domain']}'")
        print(f"   (Source: {item['source']})")

print("\n--- End of Mapping ---")
print("Review the proposed mapping above. Manually create the target YAML files (Phase 5) based on this plan.")
print("Update migration/overrides.py for any incorrect inferences and re-run this script.")
