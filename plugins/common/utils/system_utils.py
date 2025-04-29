"""
Utility functions for system-level checks and maintenance within Airflow.
"""

import os
import logging
from airflow.hooks.base import BaseHook

def check_disk_space(**kwargs):
    """
    Check disk space on the Airflow worker/scheduler node and log warning if below threshold.

    Pushes an XCom 'disk_space_warning' = True if threshold is breached.
    Assumes Airflow components run under a user with access to '/opt/airflow'.
    (Adjust path if necessary based on deployment)
    """
    logger = logging.getLogger(__name__)
    # TODO: Consider making threshold configurable via Airflow Variables
    threshold_gb = 10  # Minimum required disk space in GB
    check_path = '/opt/airflow' # Standard path, adjust if needed

    try:
        # Get disk usage statistics for the filesystem containing check_path
        stat = os.statvfs(check_path)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024 ** 3)

        if free_gb < threshold_gb:
            warning_msg = f"Low disk space on {check_path}: {free_gb:.2f} GB free, threshold is {threshold_gb} GB"
            logger.warning(warning_msg)
            # Push XCom for potential downstream alerting or conditional tasks
            kwargs['ti'].xcom_push(key='disk_space_warning', value=True)
            # Consider failing the task if space is critically low
            # raise AirflowException(warning_msg)
            return False # Indicate check failed
        else:
            logger.info(f"Disk space check passed for {check_path}: {free_gb:.2f} GB free")
            kwargs['ti'].xcom_push(key='disk_space_warning', value=False)
            return True # Indicate check passed

    except FileNotFoundError:
        logger.error(f"Path {check_path} not found for disk space check. Check configuration.")
        # Push XCom to indicate the check itself failed
        kwargs['ti'].xcom_push(key='disk_space_check_error', value=f"Path not found: {check_path}")
        raise # Re-raise exception to fail the task
    except Exception as e:
        logger.error(f"Error checking disk space for {check_path}: {str(e)}")
        kwargs['ti'].xcom_push(key='disk_space_check_error', value=str(e))
        raise # Re-raise exception to fail the task

def check_connections(**kwargs):
    """
    Check all defined Airflow connections are valid by attempting to get their hooks.

    Logs warnings for failed connections and pushes a list of failed connection IDs
    to XCom under the key 'failed_connections'.
    """
    logger = logging.getLogger(__name__)
    failed_connections = []
    # Explicitly ignore the default connection created by Airflow if unused
    ignored_conn_ids = {'airflow_db'}

    try:
        # Fetch all connections defined in Airflow
        connections = BaseHook.get_connections()
        logger.info(f"Found {len(connections)} connections to check.")

        for conn in connections:
            if conn.conn_id in ignored_conn_ids:
                logger.debug(f"Skipping check for ignored connection ID: {conn.conn_id}")
                continue

            try:
                # The core check: try to instantiate the hook for the connection
                hook = BaseHook.get_hook(conn_id=conn.conn_id)
                # Optional: Perform a lightweight test if available, e.g., hook.test_connection()
                # Be cautious as test_connection() might not exist or could be resource-intensive
                # if hasattr(hook, 'test_connection') and callable(hook.test_connection):
                #     hook.test_connection()
                logger.info(f"Connection '{conn.conn_id}' (type: {conn.conn_type}) validated successfully.")
            except Exception as e:
                # Log detailed error including connection type for easier debugging
                error_msg = f"Connection '{conn.conn_id}' (type: {conn.conn_type}) failed validation: {str(e)}"
                logger.warning(error_msg)
                failed_connections.append(conn.conn_id)

        # Push results to XCom
        kwargs['ti'].xcom_push(key='failed_connections', value=failed_connections)

        if failed_connections:
            logger.warning(f"Connection validation finished with {len(failed_connections)} failures: {failed_connections}")
            # Decide if this constitutes a task failure. Currently just logs warning.
            # return False # Uncomment to make the task fail if any connection fails
        else:
            logger.info("All checked connections validated successfully.")

        return True # Task succeeds even if connections fail (change if needed)

    except Exception as e:
        logger.error(f"An unexpected error occurred during connection checking: {str(e)}")
        kwargs['ti'].xcom_push(key='connection_check_error', value=str(e))
        raise # Re-raise exception to fail the task
