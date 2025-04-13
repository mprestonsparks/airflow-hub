"""
Validation utility functions for common data validation operations across projects.
"""

import re
import logging
from datetime import datetime


class ValidationUtils:
    """
    Utility class for data validation operations.
    
    This class provides static methods for common validation operations used across projects.
    """
    
    @staticmethod
    def validate_email(email):
        """
        Validate an email address format.
        
        Args:
            email (str): Email address to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_date_format(date_str, format_str='%Y-%m-%d'):
        """
        Validate a date string against a specified format.
        
        Args:
            date_str (str): Date string to validate.
            format_str (str, optional): Expected date format. Defaults to '%Y-%m-%d'.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            datetime.strptime(date_str, format_str)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_numeric(value, min_value=None, max_value=None):
        """
        Validate that a value is numeric and within specified range.
        
        Args:
            value: Value to validate.
            min_value (numeric, optional): Minimum allowed value. Defaults to None.
            max_value (numeric, optional): Maximum allowed value. Defaults to None.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        try:
            # Convert to float for comparison
            num_value = float(value)
            
            # Check range if specified
            if min_value is not None and num_value < min_value:
                return False
            if max_value is not None and num_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_string_length(string, min_length=None, max_length=None):
        """
        Validate that a string length is within specified range.
        
        Args:
            string (str): String to validate.
            min_length (int, optional): Minimum allowed length. Defaults to None.
            max_length (int, optional): Maximum allowed length. Defaults to None.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        if not isinstance(string, str):
            return False
        
        length = len(string)
        
        if min_length is not None and length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        
        return True
    
    @staticmethod
    def validate_in_list(value, valid_values):
        """
        Validate that a value is in a list of valid values.
        
        Args:
            value: Value to validate.
            valid_values (list): List of valid values.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        return value in valid_values
    
    @staticmethod
    def validate_dict_schema(data, schema):
        """
        Validate that a dictionary conforms to a specified schema.
        
        Args:
            data (dict): Dictionary to validate.
            schema (dict): Schema definition with field names and types.
            
        Returns:
            tuple: (bool, str) - (is_valid, error_message)
        """
        if not isinstance(data, dict):
            return False, "Data is not a dictionary"
        
        for field, field_type in schema.items():
            # Check required fields
            if field not in data:
                return False, f"Required field '{field}' is missing"
            
            # Check field type
            if not isinstance(data[field], field_type):
                return False, f"Field '{field}' should be of type {field_type.__name__}"
        
        return True, ""
    
    @staticmethod
    def validate_phone_number(phone, country_code='US'):
        """
        Validate a phone number format.
        
        Args:
            phone (str): Phone number to validate.
            country_code (str, optional): Country code for validation rules. Defaults to 'US'.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        # Simple validation for US phone numbers
        if country_code == 'US':
            # Remove common separators and spaces
            cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone)
            
            # Check if it's a 10-digit number or has country code
            if len(cleaned) == 10:
                return cleaned.isdigit()
            elif len(cleaned) == 11 and cleaned.startswith('1'):
                return cleaned.isdigit()
            else:
                return False
        
        # Add more country-specific validation as needed
        return False
    
    @staticmethod
    def validate_url(url):
        """
        Validate a URL format.
        
        Args:
            url (str): URL to validate.
            
        Returns:
            bool: True if valid, False otherwise.
        """
        pattern = r'^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def log_validation_error(logger, message, data=None):
        """
        Log a validation error with optional data.
        
        Args:
            logger (logging.Logger): Logger to use.
            message (str): Error message.
            data (any, optional): Data that failed validation. Defaults to None.
            
        Returns:
            None
        """
        if data is not None:
            logger.error(f"Validation error: {message} - Data: {data}")
        else:
            logger.error(f"Validation error: {message}")
