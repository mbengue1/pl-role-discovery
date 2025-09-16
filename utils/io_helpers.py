"""
IO helper utilities for file operations.
"""

import os
import json
import csv
import re
import logging
from typing import Dict, List, Any, Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def slugify(text: str) -> str:
    """
    Convert text to a URL-friendly slug.
    
    Args:
        text: The text to convert
        
    Returns:
        A slugified version of the text
    """
    # Convert to lowercase
    text = text.lower()
    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Remove leading/trailing hyphens
    text = text.strip('-')
    # Limit length
    return text[:50]


def ensure_directory(directory_path: str) -> None:
    """
    Ensure that the specified directory exists.
    
    Args:
        directory_path: Path to the directory
    """
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
        logger.info(f"Created directory: {directory_path}")


def read_json(file_path: str) -> Dict[str, Any]:
    """
    Read JSON from a file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Dictionary containing the JSON data
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {file_path}")
        raise


def write_json(data: Union[Dict[str, Any], List[Any]], file_path: str) -> None:
    """
    Write JSON data to a file.
    
    Args:
        data: Dictionary or list to write as JSON
        file_path: Path to the output file
    """
    # Ensure the directory exists
    ensure_directory(os.path.dirname(file_path))
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON written to: {file_path}")
    except Exception as e:
        logger.error(f"Error writing JSON to {file_path}: {str(e)}")
        raise


def read_text(file_path: str) -> str:
    """
    Read text from a file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        String containing the file contents
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise


def write_text(text: str, file_path: str) -> None:
    """
    Write text to a file.
    
    Args:
        text: Text to write
        file_path: Path to the output file
    """
    # Ensure the directory exists
    ensure_directory(os.path.dirname(file_path))
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        logger.info(f"Text written to: {file_path}")
    except Exception as e:
        logger.error(f"Error writing text to {file_path}: {str(e)}")
        raise


def write_csv(data: List[Dict[str, Any]], file_path: str, fieldnames: Optional[List[str]] = None) -> None:
    """
    Write data to a CSV file.
    
    Args:
        data: List of dictionaries to write as CSV rows
        file_path: Path to the output file
        fieldnames: Optional list of field names (columns)
    """
    # Ensure the directory exists
    ensure_directory(os.path.dirname(file_path))
    
    # If fieldnames not provided, use keys from the first dictionary
    if not fieldnames and data:
        fieldnames = list(data[0].keys())
    
    try:
        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        logger.info(f"CSV written to: {file_path}")
    except Exception as e:
        logger.error(f"Error writing CSV to {file_path}: {str(e)}")
        raise


def safe_filename(prefix: str, title: str, extension: str) -> str:
    """
    Create a safe filename with a numeric prefix.
    
    Args:
        prefix: Numeric prefix (e.g., "01")
        title: Title to convert to a slug
        extension: File extension (e.g., "json", "md")
        
    Returns:
        A safe filename
    """
    slug = slugify(title)
    return f"{prefix}_{slug}.{extension}"


def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally matching a pattern.
    
    Args:
        directory: Directory to list files from
        pattern: Optional regex pattern to match filenames
        
    Returns:
        List of file paths
    """
    if not os.path.exists(directory):
        logger.warning(f"Directory does not exist: {directory}")
        return []
    
    files = []
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            if pattern is None or re.search(pattern, filename):
                files.append(file_path)
    
    return sorted(files)
