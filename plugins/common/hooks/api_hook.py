"""
Common API hook for connecting to various REST APIs.
This hook provides a standardized interface for API connections across projects.
"""

from airflow.hooks.base import BaseHook
import requests
import logging
import json


class APIHook(BaseHook):
    """
    Hook for connecting to REST APIs using Airflow connections.
    
    This hook provides a standardized interface for API operations that can be
    used across different projects.
    
    Args:
        conn_id (str): The connection ID to use. Should follow project naming convention.
    """
    
    def __init__(self, conn_id):
        super().__init__()
        self.conn_id = conn_id
        self.connection = self.get_connection(conn_id)
        self.log = logging.getLogger(__name__)
        
        # Extract connection details
        self.base_url = self.connection.host
        if not self.base_url.startswith(('http://', 'https://')):
            self.base_url = f"https://{self.base_url}"
            
        # Handle port if specified
        if self.connection.port:
            self.base_url = f"{self.base_url}:{self.connection.port}"
            
        # Extract authentication details from connection
        self.auth_type = self.connection.extra_dejson.get('auth_type', 'none')
        
        # Validate connection naming convention
        if '_' not in conn_id:
            self.log.warning(
                f"Connection ID '{conn_id}' does not follow project naming convention: "
                "project_name_connection_purpose"
            )
    
    def get_headers(self):
        """
        Returns headers based on the authentication type.
        
        Returns:
            dict: Headers for API requests.
        """
        headers = {'Content-Type': 'application/json'}
        
        if self.auth_type == 'bearer':
            token = self.connection.password
            headers['Authorization'] = f"Bearer {token}"
        
        elif self.auth_type == 'api_key':
            api_key = self.connection.password
            key_name = self.connection.extra_dejson.get('api_key_name', 'api-key')
            headers[key_name] = api_key
        
        elif self.auth_type == 'basic':
            # Basic auth is handled by the requests library
            pass
        
        return headers
    
    def get_auth(self):
        """
        Returns auth tuple for basic authentication.
        
        Returns:
            tuple or None: (username, password) for basic auth or None for other auth types.
        """
        if self.auth_type == 'basic':
            return (self.connection.login, self.connection.password)
        return None
    
    def make_request(self, endpoint, method='GET', data=None, params=None):
        """
        Makes an API request to the specified endpoint.
        
        Args:
            endpoint (str): API endpoint (will be appended to base_url).
            method (str): HTTP method (GET, POST, PUT, DELETE).
            data (dict, optional): Request body for POST/PUT requests.
            params (dict, optional): Query parameters.
            
        Returns:
            dict: API response parsed as JSON.
            
        Raises:
            Exception: If the API request fails.
        """
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = self.get_headers()
        auth = self.get_auth()
        
        try:
            self.log.info(f"Making {method} request to {url}")
            
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params, auth=auth)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=data, params=params, auth=auth)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data, params=params, auth=auth)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, params=params, auth=auth)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Try to parse as JSON, but handle non-JSON responses
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"text": response.text}
                
        except requests.exceptions.RequestException as e:
            self.log.error(f"API request failed: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                self.log.error(f"Response status code: {e.response.status_code}")
                self.log.error(f"Response body: {e.response.text}")
            raise
