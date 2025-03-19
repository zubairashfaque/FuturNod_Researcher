# API utilities module
import logging
import hashlib
import json
import os
import uuid
from typing import Dict, Any, Optional, List, Union
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_hash(data: str) -> str:
    """
    Generate a hash for the provided data

    Args:
        data: Data to hash

    Returns:
        Hash string
    """
    return hashlib.sha256(data.encode()).hexdigest()


def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Filter a dictionary to include only specified keys

    Args:
        data: Dictionary to filter
        keys: List of keys to include

    Returns:
        Filtered dictionary
    """
    return {k: v for k, v in data.items() if k in keys}


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to a human-readable string

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    elif minutes > 0:
        return f"{int(minutes)}m {int(seconds)}s"
    else:
        return f"{seconds:.2f}s"


def format_cost(cost: float) -> str:
    """
    Format cost to a human-readable string

    Args:
        cost: Cost value

    Returns:
        Formatted cost string
    """
    if cost < 0.01:
        return f"${cost:.6f}"
    elif cost < 1:
        return f"${cost:.4f}"
    else:
        return f"${cost:.2f}"


def generate_id() -> str:
    """
    Generate a unique ID

    Returns:
        Unique ID string
    """
    return str(uuid.uuid4())


def safe_json_serialize(obj: Any) -> Any:
    """
    Safely serialize objects to JSON, handling types that aren't JSON serializable

    Args:
        obj: Object to serialize

    Returns:
        JSON-serializable object
    """
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    elif isinstance(obj, set):
        return list(obj)
    return str(obj)


def deep_merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries

    Args:
        dict1: First dictionary
        dict2: Second dictionary

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # If both values are dictionaries, merge them recursively
            result[key] = deep_merge_dicts(result[key], value)
        else:
            # Otherwise, just overwrite the value
            result[key] = value

    return result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to ensure it's safe for the filesystem

    Args:
        filename: Filename to sanitize

    Returns:
        Sanitized filename
    """
    # Replace invalid characters with underscores
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')

    # Limit length to avoid issues with filesystem limits
    max_length = 255
    if len(filename) > max_length:
        name, ext = os.path.splitext(filename)
        filename = f"{name[:max_length - len(ext) - 1]}{ext}"

    return filename


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a specified maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def flatten_dict(d: Dict[str, Any], parent_key: str = "", sep: str = "_") -> Dict[str, Any]:
    """
    Flatten a nested dictionary

    Args:
        d: Dictionary to flatten
        parent_key: Parent key for recursion
        sep: Separator for keys

    Returns:
        Flattened dictionary
    """
    items = []

    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k

        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def extract_domain(url: str) -> str:
    """
    Extract domain from URL

    Args:
        url: URL to extract domain from

    Returns:
        Domain string
    """
    try:
        from urllib.parse import urlparse

        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Remove www. prefix if present
        if domain.startswith('www.'):
            domain = domain[4:]

        return domain
    except Exception as e:
        logger.error(f"Error extracting domain from URL {url}: {str(e)}")
        return url