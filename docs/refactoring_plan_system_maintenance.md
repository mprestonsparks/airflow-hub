# Refactoring Plan: Implementing System Maintenance with Vault Secrets

## Objective

To correctly implement the system maintenance DAG (`dags/common/system_maintenance.py`) to securely access necessary secrets and environment variables using Airflow's Vault secrets backend, achieving a production-ready state.

## Identified Gaps

*   The system maintenance logic is not correctly defined or integrated with secrets management after the attempted YAML conversion.
*   The mechanism for accessing secrets/environment variables within the system maintenance tasks is broken or undefined.
*   The Airflow environment in Docker Compose may not be fully configured to utilize the Vault secrets backend as per the architecture document.
*   Vault may not be initialized or populated with the required secrets.

## Proposed Solution

Ensure the system maintenance DAG is a standard Python DAG (`dags/common/system_maintenance.py`) that retrieves any necessary sensitive information via Airflow Connections or Variables, which are configured to be sourced from HashiCorp Vault.

## Detailed Steps

1.  **Verify/Restore Python DAG:**
    *   Confirm that `dags/common/system_maintenance.py` exists and contains the intended system maintenance tasks (log cleanup, DB optimization, health checks, etc.). If the file was removed or significantly altered during the YAML conversion attempt, restore or rewrite it based on the required functionality.

2.  **Identify Secrets and Variables:**
    *   Analyze the tasks within `dags/common/system_maintenance.py`.
    *   Identify any parameters or configurations that should not be hardcoded and need to be managed as secrets or variables (e.g., database credentials for optimization, thresholds for disk space checks if they are dynamic, email addresses for notifications if they are sensitive or environment-specific).

3.  **Integrate Airflow Secrets Management in DAG:**
    *   Modify the Python DAG tasks to retrieve the identified secrets/variables using Airflow's built-in mechanisms:
        *   For database connections or external service credentials, use `BaseHook.get_connection('your_connection_id')`. Define appropriate `connection_id`s (e.g., `airflow_db_maintenance`).
        *   For other configuration values, use `Variable.get('your_variable_key')` (e.g., `system_maintenance_disk_threshold_gb`).
    *   Remove any direct references to environment variables (`os.environ.get(...)`) for sensitive information within the DAG code.

4.  **Configure Docker Environment for Vault:**
    *   Update the `docker-compose.yml` file to include the `vault` service and configure the Airflow `webserver` and `scheduler` services to use the Vault secrets backend. This involves adding the `vault` service definition and setting the `AIRFLOW__SECRETS__BACKEND` and `AIRFLOW__SECRETS__BACKEND_KWARTS` environment variables for the Airflow services, as detailed in `docs/secrets_management_architecture.md` (Phase 1).

5.  **Populate Vault with Secrets:**
    *   Ensure the necessary secrets (Connections and Variables identified in Step 2) are populated in your running Vault instance.
    *   This can be done manually via the Vault UI or CLI, or by using the initialization/migration scripts mentioned in `docs/secrets_management_architecture.md` (Phase 2), adapting them as needed for the specific secrets required by the system maintenance DAG. Follow the recommended path structure (`secret/airflow/connections/...` and `secret/airflow/variables/...`).

6.  **Testing:**
    *   **Verify Vault Connectivity:** Ensure the Vault service is healthy and accessible from the Airflow containers. The health check in `docker-compose.yml` (Phase 1, Step 3 of the architecture doc) is a good starting point. You can also use a simple `curl` command from within an Airflow container to test connectivity to Vault.
    *   **Test Airflow-Vault Integration:** Run a simple test (e.g., a small temporary DAG or a Python script executed in the Airflow environment) to confirm that Airflow can successfully retrieve a test secret from Vault using `BaseHook.get_connection` and `Variable.get`. The `scripts/test_vault_integration.py` mentioned in the architecture document (Section 4) can be adapted for this purpose.
    *   **Test DAG Execution:** Trigger the `common_system_maintenance` DAG manually in the Airflow UI. Monitor the task logs closely to ensure that secrets are being retrieved correctly and that the tasks execute without errors related to missing credentials or configuration.

## Secrets Flow

```mermaid
graph TD
    A[System Maintenance DAG Tasks] -->|Request Connection/Variable| B[Airflow Secrets Backend]
    B -->|Fetch Secret| C[HashiCorp Vault]
    C -->|Return Secret| B
    B -->|Provide Secret| A