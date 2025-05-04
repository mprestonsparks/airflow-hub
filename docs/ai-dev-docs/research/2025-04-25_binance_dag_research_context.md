## Prompt for AI Research Assistant:

Please research and recommend Airflow DAG structures, patterns, operators, and best practices specifically for building a robust and scalable ETL pipeline to extract cryptocurrency data from the Binance API. The pipeline will be part of an Airflow monorepo project that uses `dag-factory` to generate DAGs from YAML definitions.

## Context:

**1. Project Goal:**
   - Implement a comprehensive ETL pipeline for cryptocurrency market data (e.g., historical Klines/candlesticks, trades, ticker info, account balances) using the official Binance API.
   - The pipeline should handle extraction, basic transformation/cleaning, and loading into a target storage (details TBD, assume database or data lake).

**2. Project Architecture:**
   - **Airflow Monorepo:** The DAGs reside within a larger `airflow-hub` monorepo designed to manage multiple data projects.
   - **`dag-factory`:** We are using the `dag-factory` library to define DAGs declaratively in YAML files. This promotes consistency and simplifies DAG creation.
   - **Docker:** Airflow and its tasks are intended to run within Docker containers.
   - **Naming Convention:** YAML files follow a `provider_[optional_asset]_domain.yaml` structure (e.g., `binance_ingestion.yaml`, `binance_crypto_transformation.yaml`).

**3. Current Example (`binance_ingestion.yaml`):**
   - Defines an ingestion DAG for daily market data.
   - Uses the `DockerOperator` to run a containerized Python script (`market-analysis:latest`) responsible for the actual API interaction and data fetching.
   - Leverages Airflow Connections (`docker_conn_id`) for secure management of Binance API keys.
   - Uses parameters (`params`) for dynamic inputs like the trading symbol (e.g., `BTCUSDT`).
   - Example YAML Snippet:
     ```yaml
     # dags/ingestion/binance_ingestion.yaml
     default:
       dag:
         # ... standard DAG args like schedule, start_date, tags ...
         params:
           symbol: 'BTCUSDT'
       tasks:
         # ... default task args ...

     binance_crypto_ingestion:
       dag:
         description: 'Ingest daily market data from Binance via market-analysis container (YAML definition)'
         # ... other DAG properties ...
       tasks:
         ingest_market_data:
           operator: airflow.providers.docker.operators.docker.DockerOperator
           image: 'market-analysis:latest'
           docker_conn_id: binance_default 
           command: >
             python -m src.main
             --symbol {{ params.symbol }}
             # ... other potential args ...
     ```

**4. Key Considerations:**
   - **Rate Limiting:** Binance API has strict rate limits. DAGs must incorporate strategies to handle this (e.g., delays, batching, appropriate scheduling).
   - **Pagination:** Many Binance endpoints require pagination. Tasks need to handle fetching all pages of data reliably.
   - **Data Volume:** Historical data can be large. Strategies for chunking/backfilling are needed.
   - **Error Handling & Retries:** Robust error handling for API issues, network problems, etc., is crucial.
   - **Idempotency:** Tasks should ideally be idempotent.
   - **Scalability:** The design should scale to handle potentially many symbols or data types.
   - **Maintainability:** Using the YAML/`dag-factory` approach should be maintained.

**Research Request:**

Based on the context above, please provide insights and recommendations on:

1.  **Optimal DAG Granularity:** Should we have one large DAG for all Binance data, or multiple smaller DAGs (e.g., one per endpoint type, one per symbol, one per frequency)? What are the pros and cons in the context of `dag-factory`?
2.  **Recommended Operators:** Beyond `DockerOperator`, are there other standard Airflow operators (e.g., `SimpleHttpOperator`, `PythonOperator`, specific Provider operators) that are well-suited for interacting with the Binance API directly from YAML, potentially simplifying tasks?
3.  **ETL Patterns:** Common Airflow ETL patterns applicable here (e.g., staging tables, incremental loads, full refreshes, backfilling strategies).
4.  **Rate Limiting/Pagination Strategies:** How can these be effectively implemented within the DAG structure (e.g., using `PythonOperator` with delays, custom sensors, TaskGroups)?
5.  **Parameterization:** Best ways to parameterize DAGs for different symbols, date ranges, environments (dev/prod) using `dag-factory`'s capabilities.
6.  **State Management:** How to manage state effectively (e.g., tracking the last loaded date/timestamp for incremental loads)?

Please focus on practical recommendations that integrate well with the existing `dag-factory` and Docker-based architecture.
