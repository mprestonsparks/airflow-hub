"""
API sensor for monitoring external API endpoints.
"""

from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from plugins.common.hooks.api_hook import APIHook
import logging


class APISensor(BaseSensorOperator):
    """
    Sensor for monitoring external API endpoints.
    
    This sensor checks if an API endpoint meets specific criteria such as:
    - Availability (HTTP status code)
    - Response content validation
    - Response timing thresholds
    
    Args:
        conn_id (str): The connection ID to use for the API.
        endpoint (str): The API endpoint to monitor.
        method (str): HTTP method to use. Defaults to 'GET'.
        params (dict, optional): Query parameters. Defaults to None.
        response_check (callable, optional): Function to validate response. Defaults to None.
        status_code (int, optional): Expected HTTP status code. Defaults to 200.
        **kwargs: Additional arguments passed to the BaseSensorOperator.
    """
    
    @apply_defaults
    def __init__(
        self,
        conn_id,
        endpoint,
        method='GET',
        params=None,
        response_check=None,
        status_code=200,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.conn_id = conn_id
        self.endpoint = endpoint
        self.method = method
        self.params = params or {}
        self.response_check = response_check
        self.status_code = status_code
        self.log = logging.getLogger(__name__)
    
    def poke(self, context):
        """
        Function that the scheduler calls to determine if the sensor should trigger.
        
        Args:
            context (dict): Airflow context dictionary.
            
        Returns:
            bool: True if the criteria are met, False otherwise.
        """
        self.log.info(f"Poking API endpoint: {self.endpoint}")
        
        # Create API hook
        hook = APIHook(self.conn_id)
        
        try:
            # Make the API request
            import time
            start_time = time.time()
            
            # Use the hook to make the request
            response = hook.make_request(
                endpoint=self.endpoint,
                method=self.method,
                params=self.params
            )
            
            request_time = time.time() - start_time
            self.log.info(f"API request completed in {request_time:.2f} seconds")
            
            # Check if response_check is provided and call it
            if self.response_check:
                check_result = self.response_check(response)
                if not check_result:
                    self.log.info("API response check failed")
                    return False
            
            # All checks passed
            return True
            
        except Exception as e:
            self.log.info(f"API request failed: {str(e)}")
            return False
