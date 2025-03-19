# Request data models
from pydantic import BaseModel, Field, validator
import re
from typing import Optional


class ResearchRequest(BaseModel):
    """Model for research request data"""
    query: str = Field(..., min_length=3, max_length=500, description="Research query")
    report_type: str = Field("research_report", description="Type of report to generate")

    @validator('query')
    def validate_query(cls, v):
        # Remove any potential malicious input or injection attempts
        # Basic sanitization - remove suspicious patterns
        sanitized = re.sub(r'[;\'"\\]', '', v)

        # Check for potential prompt injection attempts
        injection_patterns = [
            r'ignore previous instructions',
            r'disregard',
            r'ignore all',
            r'system prompt',
            r'user prompt'
        ]

        for pattern in injection_patterns:
            if re.search(pattern, sanitized.lower()):
                raise ValueError(f"Query contains potential prompt injection pattern")

        return sanitized

    @validator('report_type')
    def validate_report_type(cls, v):
        valid_types = ["research_report", "blog_post", "outline", "summary"]
        if v not in valid_types:
            raise ValueError(f"Report type must be one of: {', '.join(valid_types)}")
        return v


class AuthRequest(BaseModel):
    """Model for authentication requests"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)