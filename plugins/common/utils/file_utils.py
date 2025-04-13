"""
File utility functions for common file operations across projects.
"""

import os
import csv
import json
import logging
from pathlib import Path


class FileUtils:
    """
    Utility class for file operations.
    
    This class provides static methods for common file operations used across projects.
    """
    
    @staticmethod
    def ensure_dir_exists(directory_path):
        """
        Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory_path (str): Path to the directory.
            
        Returns:
            str: Path to the directory.
        """
        os.makedirs(directory_path, exist_ok=True)
        return directory_path
    
    @staticmethod
    def list_files(directory_path, pattern=None, recursive=False):
        """
        List files in a directory, optionally filtering by pattern.
        
        Args:
            directory_path (str): Path to the directory.
            pattern (str, optional): File pattern to match (e.g., '*.csv'). Defaults to None.
            recursive (bool, optional): Whether to search recursively. Defaults to False.
            
        Returns:
            list: List of file paths.
        """
        path = Path(directory_path)
        
        if not recursive:
            # Non-recursive search
            if pattern:
                return [str(f) for f in path.glob(pattern) if f.is_file()]
            else:
                return [str(f) for f in path.iterdir() if f.is_file()]
        else:
            # Recursive search
            if pattern:
                return [str(f) for f in path.glob(f"**/{pattern}") if f.is_file()]
            else:
                return [str(f) for f in path.glob("**/*") if f.is_file()]
    
    @staticmethod
    def read_csv(file_path, delimiter=',', has_header=True):
        """
        Read a CSV file into a list of dictionaries or lists.
        
        Args:
            file_path (str): Path to the CSV file.
            delimiter (str, optional): CSV delimiter. Defaults to ','.
            has_header (bool, optional): Whether the CSV has a header row. Defaults to True.
            
        Returns:
            list: List of dictionaries (if has_header=True) or lists (if has_header=False).
        """
        result = []
        
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            if has_header:
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                for row in reader:
                    result.append(row)
            else:
                reader = csv.reader(csvfile, delimiter=delimiter)
                for row in reader:
                    result.append(row)
        
        return result
    
    @staticmethod
    def write_csv(file_path, data, fieldnames=None, delimiter=',', append=False):
        """
        Write data to a CSV file.
        
        Args:
            file_path (str): Path to the CSV file.
            data (list): List of dictionaries or lists to write.
            fieldnames (list, optional): List of field names for the header.
                Required if data is a list of dictionaries and not appending.
            delimiter (str, optional): CSV delimiter. Defaults to ','.
            append (bool, optional): Whether to append to existing file. Defaults to False.
            
        Returns:
            bool: True if successful.
        """
        mode = 'a' if append else 'w'
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, mode, newline='', encoding='utf-8') as csvfile:
            if isinstance(data[0], dict):
                # If fieldnames not provided, use keys from first dictionary
                if fieldnames is None:
                    fieldnames = data[0].keys()
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=delimiter)
                
                # Write header only if not appending or file is empty
                if not append or os.path.getsize(file_path) == 0:
                    writer.writeheader()
                
                writer.writerows(data)
            else:
                writer = csv.writer(csvfile, delimiter=delimiter)
                writer.writerows(data)
        
        return True
    
    @staticmethod
    def read_json(file_path):
        """
        Read a JSON file.
        
        Args:
            file_path (str): Path to the JSON file.
            
        Returns:
            dict or list: Parsed JSON data.
        """
        with open(file_path, 'r', encoding='utf-8') as jsonfile:
            return json.load(jsonfile)
    
    @staticmethod
    def write_json(file_path, data, pretty=True):
        """
        Write data to a JSON file.
        
        Args:
            file_path (str): Path to the JSON file.
            data (dict or list): Data to write.
            pretty (bool, optional): Whether to format with indentation. Defaults to True.
            
        Returns:
            bool: True if successful.
        """
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as jsonfile:
            if pretty:
                json.dump(data, jsonfile, indent=2)
            else:
                json.dump(data, jsonfile)
        
        return True
    
    @staticmethod
    def get_file_size(file_path):
        """
        Get the size of a file in bytes.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            int: File size in bytes.
        """
        return os.path.getsize(file_path)
    
    @staticmethod
    def get_file_modification_time(file_path):
        """
        Get the last modification time of a file.
        
        Args:
            file_path (str): Path to the file.
            
        Returns:
            float: Modification time as a timestamp.
        """
        return os.path.getmtime(file_path)
    
    @staticmethod
    def move_file(source_path, destination_path, overwrite=False):
        """
        Move a file from source to destination.
        
        Args:
            source_path (str): Source file path.
            destination_path (str): Destination file path.
            overwrite (bool, optional): Whether to overwrite existing file. Defaults to False.
            
        Returns:
            bool: True if successful.
            
        Raises:
            FileExistsError: If destination exists and overwrite=False.
        """
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(destination_path)), exist_ok=True)
        
        # Check if destination exists
        if os.path.exists(destination_path) and not overwrite:
            raise FileExistsError(f"Destination file already exists: {destination_path}")
        
        # Move the file
        os.replace(source_path, destination_path)
        return True
