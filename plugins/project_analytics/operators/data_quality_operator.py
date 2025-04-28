"""
Data quality operator for validating data quality checks.
"""

from airflow.models.baseoperator import BaseOperator
from plugins.common.operators.base_operator import BaseDataOperator
import logging
import pandas as pd
import numpy as np


class DataQualityOperator(BaseDataOperator):
    """
    Operator for performing data quality checks on datasets.
    
    This operator runs a series of data quality checks on a dataset and
    raises an exception if any of the checks fail.
    
    Args:
        conn_id (str): Connection ID for the data source.
        table (str): Table or dataset name to check.
        checks (list): List of data quality check dictionaries.
        sql_query (str, optional): Custom SQL query to fetch data. If None, will query the entire table.
        fail_on_error (bool, optional): Whether to fail the task if checks fail. Defaults to True.
        validate_conn_id (bool, optional): Whether to validate the connection ID. Defaults to True.
        **kwargs: Additional arguments passed to the BaseDataOperator.
    """
    
    template_fields = ('table', 'sql_query')
    
    def __init__(
        self,
        conn_id,
        table,
        checks,
        sql_query=None,
        fail_on_error=True,
        validate_conn_id=True,
        **kwargs
    ):
        # Call super() WITHOUT conn_id, passing other kwargs (like task_id) up
        super().__init__(**kwargs)

        # Set conn_id *after* BaseOperator initialization
        self.conn_id = conn_id
        
        # Perform validation *after* BaseOperator has set self.conn_id
        if validate_conn_id:
            self._validate_conn_id(self.conn_id)
        
        # Restore templated field assignments
        self.table = table
        self.checks = checks
        self.sql_query = sql_query
        self.fail_on_error = fail_on_error
    
    def execute(self, context):
        """
        Execute the data quality checks.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            dict: Results of the data quality checks.
            
        Raises:
            ValueError: If any checks fail and fail_on_error is True.
        """
        self.log.info(f"Running data quality checks on {self.table}")
        
        # Get database hook
        from plugins.common.hooks.database_hook import DatabaseHook
        hook = DatabaseHook(self.conn_id)
        
        # Fetch data
        if self.sql_query:
            query = self.sql_query
        else:
            query = f"SELECT * FROM {self.table}"
        
        self.log.info(f"Executing query: {query}")
        results = hook.run_query(query)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(results)
        
        if df.empty:
            message = f"No data found in {self.table}"
            self.log.warning(message)
            if self.fail_on_error:
                raise ValueError(message)
            return {"passed": False, "message": message}
        
        # Run all checks
        check_results = []
        all_passed = True
        
        for check in self.checks:
            check_type = check.get('type')
            check_result = {"type": check_type, "passed": False}
            
            try:
                if check_type == 'not_null':
                    # Check for null values in specified columns
                    columns = check.get('columns', [])
                    for column in columns:
                        if column not in df.columns:
                            raise ValueError(f"Column {column} not found in dataset")
                        
                        null_count = df[column].isnull().sum()
                        if null_count > 0:
                            check_result["message"] = f"Column {column} has {null_count} null values"
                            all_passed = False
                            break
                    else:
                        check_result["passed"] = True
                
                elif check_type == 'unique':
                    # Check for uniqueness in specified columns
                    columns = check.get('columns', [])
                    for column in columns:
                        if column not in df.columns:
                            raise ValueError(f"Column {column} not found in dataset")
                        
                        unique_count = df[column].nunique()
                        total_count = len(df)
                        
                        if unique_count != total_count:
                            check_result["message"] = f"Column {column} has {total_count - unique_count} duplicate values"
                            all_passed = False
                            break
                    else:
                        check_result["passed"] = True
                
                elif check_type == 'value_range':
                    # Check if values are within specified range
                    column = check.get('column')
                    min_value = check.get('min')
                    max_value = check.get('max')
                    
                    if column not in df.columns:
                        raise ValueError(f"Column {column} not found in dataset")
                    
                    if min_value is not None and df[column].min() < min_value:
                        check_result["message"] = f"Column {column} has values less than {min_value}"
                        all_passed = False
                    elif max_value is not None and df[column].max() > max_value:
                        check_result["message"] = f"Column {column} has values greater than {max_value}"
                        all_passed = False
                    else:
                        check_result["passed"] = True
                
                elif check_type == 'custom_sql':
                    # Run custom SQL check
                    sql = check.get('sql')
                    expected_result = check.get('expected_result')
                    
                    custom_result = hook.run_query(sql)
                    
                    if custom_result != expected_result:
                        check_result["message"] = f"Custom SQL check failed. Expected {expected_result}, got {custom_result}"
                        all_passed = False
                    else:
                        check_result["passed"] = True
                
                elif check_type == 'row_count':
                    # Check row count constraints
                    min_rows = check.get('min_rows')
                    max_rows = check.get('max_rows')
                    row_count = len(df)
                    
                    if min_rows is not None and row_count < min_rows:
                        check_result["message"] = f"Row count {row_count} is less than minimum {min_rows}"
                        all_passed = False
                    elif max_rows is not None and row_count > max_rows:
                        check_result["message"] = f"Row count {row_count} is greater than maximum {max_rows}"
                        all_passed = False
                    else:
                        check_result["passed"] = True
                
                else:
                    check_result["message"] = f"Unknown check type: {check_type}"
                    all_passed = False
            
            except Exception as e:
                check_result["message"] = f"Error running check: {str(e)}"
                all_passed = False
            
            check_results.append(check_result)
        
        # Compile final results
        final_results = {
            "table": self.table,
            "passed": all_passed,
            "checks": check_results
        }
        
        # Log results
        if all_passed:
            self.log.info(f"All data quality checks passed for {self.table}")
        else:
            failed_checks = [c for c in check_results if not c["passed"]]
            self.log.warning(f"{len(failed_checks)} data quality checks failed for {self.table}")
            for check in failed_checks:
                self.log.warning(f"Failed check: {check['type']} - {check.get('message', 'No message')}")
            
            if self.fail_on_error:
                raise ValueError(f"Data quality checks failed for {self.table}")
        
        return final_results
