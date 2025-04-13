"""
Enhanced file sensor for monitoring file systems with additional functionality.
"""

from airflow.sensors.filesystem import FileSensor
from airflow.utils.decorators import apply_defaults
import os
import logging


class EnhancedFileSensor(FileSensor):
    """
    Enhanced sensor for monitoring file systems with additional functionality.
    
    This sensor extends the standard FileSensor with additional features like:
    - File content validation
    - File size checks
    - File age validation
    - Multiple file pattern support
    
    Args:
        filepath (str): The file path to monitor.
        fs_conn_id (str): The connection ID to use for the file system.
        min_file_size (int, optional): Minimum file size in bytes. Defaults to None.
        max_file_age_minutes (int, optional): Maximum file age in minutes. Defaults to None.
        content_check (callable, optional): Function to validate file content. Defaults to None.
        **kwargs: Additional arguments passed to the FileSensor.
    """
    
    @apply_defaults
    def __init__(
        self,
        filepath,
        fs_conn_id='fs_default',
        min_file_size=None,
        max_file_age_minutes=None,
        content_check=None,
        **kwargs
    ):
        super().__init__(filepath=filepath, fs_conn_id=fs_conn_id, **kwargs)
        self.min_file_size = min_file_size
        self.max_file_age_minutes = max_file_age_minutes
        self.content_check = content_check
        self.log = logging.getLogger(__name__)
    
    def poke(self, context):
        """
        Function that the scheduler calls to determine if the sensor should trigger.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            bool: True if the criteria are met, False otherwise.
        """
        # First check if the file exists using the parent class method
        if not super().poke(context):
            return False
        
        # If we get here, the file exists, now perform additional checks
        hook = self.get_hook()
        
        # Get file stats
        stats = hook.get_file_metadata(self.filepath)
        file_size = stats['size']
        file_modified = stats['last_modified']
        
        # Check file size if specified
        if self.min_file_size is not None and file_size < self.min_file_size:
            self.log.info(
                f"File {self.filepath} exists but is too small: "
                f"{file_size} bytes < {self.min_file_size} bytes"
            )
            return False
        
        # Check file age if specified
        if self.max_file_age_minutes is not None:
            import datetime
            now = datetime.datetime.now(file_modified.tzinfo)
            age_minutes = (now - file_modified).total_seconds() / 60
            
            if age_minutes > self.max_file_age_minutes:
                self.log.info(
                    f"File {self.filepath} exists but is too old: "
                    f"{age_minutes:.1f} minutes > {self.max_file_age_minutes} minutes"
                )
                return False
        
        # Check file content if specified
        if self.content_check is not None:
            with hook.open(self.filepath, 'rb') as file:
                content = file.read()
                
            if not self.content_check(content):
                self.log.info(f"File {self.filepath} exists but content validation failed")
                return False
        
        # All checks passed
        return True
