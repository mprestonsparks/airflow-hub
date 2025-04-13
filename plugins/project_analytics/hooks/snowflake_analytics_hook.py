"""
Snowflake analytics hook for advanced analytics operations.
"""

from airflow.hooks.base import BaseHook
import logging
import pandas as pd
import snowflake.connector
from typing import List, Dict, Any, Optional, Union


class SnowflakeAnalyticsHook(BaseHook):
    """
    Hook for connecting to Snowflake with advanced analytics capabilities.
    
    This hook extends the basic database functionality with analytics-specific
    methods for data transformation, aggregation, and analysis.
    
    Args:
        conn_id (str): Connection ID for Snowflake. Should follow project naming convention.
    """
    
    def __init__(self, conn_id: str):
        super().__init__()
        self.conn_id = conn_id
        self.connection = self.get_connection(conn_id)
        self.log = logging.getLogger(__name__)
        
        # Validate connection naming convention
        if not conn_id.startswith('project_analytics_'):
            self.log.warning(
                f"Connection ID '{conn_id}' does not follow project naming convention: "
                "project_analytics_*"
            )
    
    def get_conn(self):
        """
        Returns a Snowflake connection object.
        
        Returns:
            snowflake.connector.connection.SnowflakeConnection: A Snowflake connection.
        """
        # Extract connection details
        account = self.connection.host
        user = self.connection.login
        password = self.connection.password
        database = self.connection.schema
        
        # Extract additional parameters from extras
        extras = self.connection.extra_dejson
        warehouse = extras.get('warehouse')
        role = extras.get('role')
        
        # Create connection
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            database=database,
            warehouse=warehouse,
            role=role
        )
        
        return conn
    
    def run_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as a list of dictionaries.
        
        Args:
            sql (str): SQL query to execute.
            params (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            list: List of dictionaries representing query results.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params or {})
            
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
    
    def run_analytics_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as a pandas DataFrame for analytics.
        
        Args:
            sql (str): SQL query to execute.
            params (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            pandas.DataFrame: DataFrame containing query results.
        """
        conn = self.get_conn()
        
        try:
            # Use pandas read_sql to directly get a DataFrame
            df = pd.read_sql(sql, conn, params=params or {})
            return df
        
        finally:
            conn.close()
    
    def execute_query(self, sql: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a SQL query without returning results (for INSERT, UPDATE, DELETE).
        
        Args:
            sql (str): SQL query to execute.
            params (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            int: Number of affected rows.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute(sql, params or {})
            conn.commit()
            return cursor.rowcount
        
        finally:
            cursor.close()
            conn.close()
    
    def run_stored_procedure(self, procedure_name: str, params: Optional[List[Any]] = None) -> Any:
        """
        Execute a stored procedure.
        
        Args:
            procedure_name (str): Name of the stored procedure.
            params (list, optional): Parameters for the stored procedure. Defaults to None.
            
        Returns:
            Any: Result of the stored procedure.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            if params:
                result = cursor.execute(f"CALL {procedure_name}(%s)", params)
            else:
                result = cursor.execute(f"CALL {procedure_name}()")
            
            return result.fetchone()[0]
        
        finally:
            cursor.close()
            conn.close()
    
    def create_temp_table(self, table_name: str, df: pd.DataFrame) -> None:
        """
        Create a temporary table from a pandas DataFrame.
        
        Args:
            table_name (str): Name for the temporary table.
            df (pandas.DataFrame): DataFrame to load into the table.
        """
        conn = self.get_conn()
        cursor = conn.cursor()
        
        try:
            # Generate column definitions
            columns = []
            for col_name, dtype in df.dtypes.items():
                if pd.api.types.is_integer_dtype(dtype):
                    col_type = "INTEGER"
                elif pd.api.types.is_float_dtype(dtype):
                    col_type = "FLOAT"
                elif pd.api.types.is_datetime64_dtype(dtype):
                    col_type = "TIMESTAMP"
                elif pd.api.types.is_bool_dtype(dtype):
                    col_type = "BOOLEAN"
                else:
                    col_type = "VARCHAR(16777216)"  # Snowflake max VARCHAR size
                
                columns.append(f'"{col_name}" {col_type}')
            
            # Create temporary table
            create_sql = f"""
            CREATE OR REPLACE TEMPORARY TABLE {table_name} (
                {', '.join(columns)}
            )
            """
            cursor.execute(create_sql)
            
            # Insert data
            placeholders = ', '.join(['%s'] * len(df.columns))
            insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples for insertion
            data = [tuple(row) for row in df.values]
            cursor.executemany(insert_sql, data)
            
            conn.commit()
            self.log.info(f"Created temporary table {table_name} with {len(df)} rows")
        
        finally:
            cursor.close()
            conn.close()
    
    def run_time_series_analysis(self, sql: str, date_column: str, value_column: str, 
                                params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run time series analysis on data from a SQL query.
        
        Args:
            sql (str): SQL query to fetch time series data.
            date_column (str): Name of the date/timestamp column.
            value_column (str): Name of the value column to analyze.
            params (dict, optional): Query parameters. Defaults to None.
            
        Returns:
            dict: Dictionary containing time series analysis results.
        """
        # Fetch data as DataFrame
        df = self.run_analytics_query(sql, params)
        
        if df.empty:
            return {"error": "No data returned from query"}
        
        # Ensure date column is datetime type
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Set date as index
        df = df.set_index(date_column)
        
        # Basic time series analysis
        analysis = {
            "total_points": len(df),
            "date_range": {
                "start": df.index.min().strftime('%Y-%m-%d'),
                "end": df.index.max().strftime('%Y-%m-%d')
            },
            "statistics": {
                "mean": float(df[value_column].mean()),
                "median": float(df[value_column].median()),
                "std_dev": float(df[value_column].std()),
                "min": float(df[value_column].min()),
                "max": float(df[value_column].max())
            }
        }
        
        # Add resampling analysis if enough data points
        if len(df) >= 10:
            # Monthly aggregation
            monthly = df.resample('M').mean()
            analysis["monthly_avg"] = {
                date.strftime('%Y-%m'): float(value) 
                for date, value in zip(monthly.index, monthly[value_column])
            }
            
            # Detect trend (simple linear regression)
            try:
                from scipy import stats
                import numpy as np
                
                # Create numeric X values (days since start)
                x = np.array((df.index - df.index.min()).total_seconds() / (24*3600))
                y = df[value_column].values
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                
                analysis["trend"] = {
                    "slope": float(slope),
                    "r_squared": float(r_value**2),
                    "p_value": float(p_value),
                    "direction": "increasing" if slope > 0 else "decreasing"
                }
            except Exception as e:
                self.log.warning(f"Could not calculate trend: {str(e)}")
        
        return analysis
