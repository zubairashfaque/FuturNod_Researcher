#!/usr/bin/env python
import re
import logging
import html
import os
import secrets
from typing import Dict, Any, Union, List, Optional
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger("security_utils")

class InputSanitizer:
    """
    Utility class for sanitizing and validating input data to prevent security issues
    like SQL injection, XSS, and prompt injection.
    """
    
    # Patterns to detect potentially malicious input
    DANGEROUS_PATTERNS = [
        r'<script.*?>.*?</script>',  # JavaScript tags
        r'javascript:',              # JavaScript protocol
        r'on\w+\s*=',                # Event handlers
        r'<!--.*?-->',               # HTML comments
        r'<iframe.*?>.*?</iframe>',  # iframes
        r'\b(ALTER|CREATE|DELETE|DROP|EXEC|INSERT|SELECT|UPDATE|UNION)\b.*?;', # SQL commands
        r'\b(system|exec|eval|spawn|require|subprocess)\s*\(',  # Command execution functions
        r'(`|\$\(|\/bin\/|\||\&\&|\|\|)',  # Shell commands/operators
        r'\/etc\/(passwd|shadow|hosts)',  # Sensitive system files
        r'(ignore previous instructions|ignore all instructions|disregard|forget about|bypass)',  # Prompt injection attempts
    ]
    
    @classmethod
    def sanitize_input(cls, data: Any) -> Any:
        """
        Sanitize the input data to prevent security issues.
        
        Args:
            data: Input data (can be a dictionary, list, string, or other primitive)
            
        Returns:
            Sanitized data of the same type
        """
        if isinstance(data, dict):
            return {k: cls.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_input(item) for item in data]
        elif isinstance(data, str):
            return cls._sanitize_string(data)
        else:
            # For other primitives (int, bool, etc.), return as is
            return data
    
    @classmethod
    def _sanitize_string(cls, text: str) -> str:
        """
        Sanitize a string value.
        
        Args:
            text: Input text string
            
        Returns:
            Sanitized text string
        """
        # Trim whitespace
        sanitized = text.strip()
        
        # Check for dangerous patterns
        dangerous_pattern_found = False
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                logger.warning(f"Dangerous pattern found in input: '{pattern}'")
                dangerous_pattern_found = True
                sanitized = re.sub(pattern, '[FILTERED]', sanitized, flags=re.IGNORECASE)
        
        # Apply HTML escaping to prevent XSS
        sanitized = html.escape(sanitized)
        
        # Log if we made changes
        if sanitized != text:
            logger.info("Input was sanitized")
            if dangerous_pattern_found:
                logger.warning("Potentially malicious input was detected and sanitized")
        
        return sanitized
    
    @classmethod
    def validate_query(cls, query: str) -> bool:
        """
        Validate a research query for safety.
        
        Args:
            query: Research query string
            
        Returns:
            True if query is valid, False otherwise
        """
        # Basic validation: non-empty and reasonable length
        if not query or len(query) < 3:
            logger.warning("Query is too short")
            return False
        
        if len(query) > 1000:
            logger.warning("Query is too long")
            return False
        
        # Check for too many special characters
        special_char_count = sum(1 for c in query if not c.isalnum() and not c.isspace())
        if special_char_count / len(query) > 0.3:  # More than 30% special characters
            logger.warning("Query contains too many special characters")
            return False
        
        # Check for potentially harmful queries
        harmful_topics = [
            "hack", "exploit", "illegal", "bomb", "weapon", "pornography", 
            "terrorist", "child abuse", "assassination", "steal", "crack password",
        ]
        
        lower_query = query.lower()
        for topic in harmful_topics:
            if topic in lower_query:
                logger.warning(f"Query contains potentially harmful topic: {topic}")
                return False
        
        return True
    
    @classmethod
    def validate_report_type(cls, report_type: str) -> bool:
        """
        Validate that the report type is one of the allowed values.
        
        Args:
            report_type: The report type string
            
        Returns:
            True if report type is valid, False otherwise
        """
        allowed_report_types = [
            "research_report", "executive_summary", "comprehensive_analysis",
            "bullet_points", "blog_post", "investment_analysis", "market_analysis",
            "comparison", "pros_and_cons", "technical_deep_dive"
        ]
        
        if report_type not in allowed_report_types:
            logger.warning(f"Invalid report type: {report_type}")
            return False
        
        return True

# Create a singleton instance
sanitizer = InputSanitizer()

# Setup API key authentication
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Get API keys from environment
def get_api_keys() -> List[str]:
    """Get API keys from environment variables."""
    api_keys = os.getenv("API_KEYS", "").split(",")
    if not api_keys or api_keys[0] == "":
        # Generate a random API key if none is provided
        default_key = secrets.token_urlsafe(32)
        api_keys = [default_key]
        logger.warning(f"No API keys found in environment. Using generated key: {default_key}")
    return api_keys

# Authentication dependency
async def verify_api_key(request: Request, api_key: Optional[str] = Depends(api_key_header)) -> str:
    """
    Verify the API key for authentication.
    
    Args:
        request: FastAPI request object
        api_key: API key from header
        
    Returns:
        The API key if valid
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    if api_key not in get_api_keys():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    return api_key
