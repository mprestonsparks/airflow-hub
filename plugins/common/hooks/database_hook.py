"""
Common database hook for connecting to various database systems.
This hook provides a standardized interface for database connections across projects.
"""

from airflow.hooks.base import BaseHook
import logging


class DatabaseHook(BaseHook):
    """
    Hook for connecting to various database systems using Airflow connections.
    
    This hook provides a standardized interface for database operations that can be
    used across different projects. It supports various database types through
    connection type detection.
    
    Args:
        conn_id (str): The connection ID to use. Should follow project naming convention.
    """
    
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id
        self.connection = self.get_connection(conn_id)
        self.log = logging.getLogger(__name__)
        
        # Validate connection naming convention
        if '_' not in conn_id:
            self.log.warning(
                f"Connection ID '{conn_id}' does not follow project naming convention: "
                "project_name_connection_purpose"
            )
    
    def get_conn(self):
        """
        Returns a connection object based on the connection type.
        
        Returns:
            object: A connection object for the specified database type.
        """
        conn_type = self.connection.conn_type
        
        if conn_type == 'postgres':
            import psycopg2
            return psycopg2.connect(
                host=self.connection.host,
                port=self.connection.port,
                user=self.connection.login,
                password=self.connection.password,
                dbname=self.connection.schema
            )
        
        elif conn_type == 'mysql':
            import pymysql
            return pymysql.connect(
                host=self.connection.host,
                port=self.connection.port,
                user=self.connection.login,
                password=self.connection.password,
                database=self.connection.schema
            )
        
        elif conn_type == 'snowflake':
            import snowflake.connector
            return snowflake.connector.connect(
                user=self.connection.login,
                password=self.connection.password,
                account=self.connection.host,
                database=self.connection.schema,
                warehouse=self.connection.extra_dejson.get('warehouse'),
                role=self.connection.extra_dejson.get('role')
            )
        
        else:
            raise ValueError(f"Unsupported connection type: {conn_type}")
    
    def run_query(self, sql, parameters=None):
        """
        Executes a SQL query and returns the results.
        
        Args:
            sql (str): The SQL query to execute.
            parameters (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            list: A list of dictionaries representing the query results.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, parameters or {})
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch results and convert to list of dictionaries
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
        
        finally:
            cursor.close()
            conn.close()
    
    def execute_query(self, sql, parameters=None):
        """
        Executes a SQL query without returning results (for INSERT, UPDATE, DELETE).
        
        Args:
            sql (str): The SQL query to execute.
            parameters (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            int: Number of affected rows.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, parameters or {})
            conn.commit()
            return cursor.rowcount
        
        finally:
            cursor.close()
            conn.close()
