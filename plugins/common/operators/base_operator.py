"""
Base operator for data processing tasks that can be extended by project-specific operators.
"""

from airflow.models.baseoperator import BaseOperator
from airflow.utils.decorators import apply_defaults
import logging


class BaseDataOperator(BaseOperator):
    """
    Base operator for data processing tasks that provides common functionality.
    
    This operator serves as a foundation for project-specific operators and implements
    common patterns and utilities that can be shared across projects.
    
    Args:
        conn_id (str): The connection ID to use. Should follow project naming convention.
        **kwargs: Additional arguments passed to the BaseOperator.
    """
    
    @apply_defaults
    def __init__(
        self,
        conn_id=None,
        validate_conn_id=True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.validate_conn_id = validate_conn_id
        
        # Validate connection ID naming convention if specified
        if conn_id and validate_conn_id:
            self._validate_conn_id(conn_id)
    
    def _validate_conn_id(self, conn_id):
        """
        Validates that the connection ID follows project naming conventions.
        
        Args:
            conn_id (str): The connection ID to validate.
        """
        if '_' not in conn_id:
            self.log.warning(
                f"Connection ID '{conn_id}' does not follow project naming convention: "
                "project_name_connection_purpose"
            )
    
    def pre_execute(self, context):
        """
        Hook called before task execution.
        
        Args:
            context (dict): Airflow context dictionary.
        """
        self.log.info(f"Starting execution of {self.task_id}")
        
        # Additional pre-execution steps can be implemented by subclasses
        
    def post_execute(self, context, result=None):
        """
        Hook called after task execution.
        
        Args:
            context (dict): Airflow context dictionary.
            result: The result of the task execution.
        """
        self.log.info(f"Completed execution of {self.task_id}")
        
        # Additional post-execution steps can be implemented by subclasses
    
    def execute(self, context):
        """
        Main execution method that should be overridden by subclasses.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            Any: The result of the task execution.
            
        Raises:
            NotImplementedError: If not overridden by subclass.
        """
        raise NotImplementedError("Subclasses must implement execute method")
    
    def on_kill(self):
        """
        Override this method to clean up subprocesses when a task is killed.
        """
        self.log.info(f"Task {self.task_id} was killed")
        
        # Additional cleanup steps can be implemented by subclasses
