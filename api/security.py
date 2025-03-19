# API security module
import re
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from api.config import SECURITY_CONFIG

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security checks and input validation"""

    async def dispatch(self, request: Request, call_next):
        # Get request path and method
        path = request.url.path
        method = request.method

        # Skip security checks for certain paths (e.g., docs, static files)
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/static"):
            return await call_next(request)

        # Additional request validation can be added here
        # For example, check for suspicious patterns in headers, query params, etc.

        # Continue processing the request
        response = await call_next(request)

        # Add security headers to response
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


def setup_security_middleware(app: FastAPI):
    """Set up security middleware for the FastAPI application"""
    # Add HTTPS redirect middleware if SSL is enabled
    if SECURITY_CONFIG["ssl_enabled"]:
        app.add_middleware(HTTPSRedirectMiddleware)

    # Add custom security middleware
    app.add_middleware(SecurityMiddleware)


def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks

    Args:
        input_str: Input string to sanitize

    Returns:
        Sanitized string
    """
    # Basic sanitization - remove suspicious patterns
    sanitized = re.sub(r'[;\'"\\]', '', input_str)

    return sanitized


def check_for_injection(input_str: str) -> bool:
    """
    Check if input contains potential injection patterns

    Args:
        input_str: Input string to check

    Returns:
        True if injection patterns are found, False otherwise
    """
    # List of potential prompt injection patterns
    injection_patterns = [
        r'ignore previous instructions',
        r'disregard',
        r'ignore all',
        r'system prompt',
        r'user prompt'
    ]

    # Check for patterns
    for pattern in injection_patterns:
        if re.search(pattern, input_str.lower()):
            return True

    return False


def validate_and_sanitize_input(input_str: str) -> str:
    """
    Validate and sanitize user input

    Args:
        input_str: Input string to validate and sanitize

    Returns:
        Sanitized string

    Raises:
        HTTPException: If input contains potential injection patterns
    """
    # Check for injection patterns
    if check_for_injection(input_str):
        logger.warning(f"Potential prompt injection detected: {input_str}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input detected"
        )

    # Sanitize the input
    sanitized = sanitize_input(input_str)

    return sanitized