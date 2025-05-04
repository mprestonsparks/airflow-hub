# migration/overrides.py
# Define manual overrides for DAGs where automatic inference fails.
# See (2025-04-23) DAG_RESTRUCTURE_PLAN.md § 8
MIGRATION_MANUAL_OVERRIDES = {
    # Example:
    # "dags/old/path/legacy_crypto_ingest.py": {
    #    "provider": "kraken",
    #    "asset": "spot",
    #    "domain": "ingestion"
    # },
    # Add real overrides below as needed during migration
    "dags/market-analysis/dag_market_analysis_ingestion.py": {
        # "provider": "marketdata",  # Incorrect - uses Binance creds
        "provider": "binance",
        "asset": None,          # Assuming no specific asset class
        "domain": "ingestion"
    }
}
