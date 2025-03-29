# Request data models
from pydantic import BaseModel, Field, validator
import re
from typing import Optional


class ResearchRequest(BaseModel):
    """Model for research request data"""
    query: str = Field(..., min_length=3, max_length=500, description="Research query")
    report_type: str = Field("research_report", description="Type of report to generate")
    tone: Optional[str] = Field("objective", description="Tone of the research report")

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
        valid_types = [
            "research_report",  # Summary - Short and fast
            "detailed_report",  # Detailed - In depth and longer
            "resource_report",
            "outline_report",
            "custom_report",
            "subtopic_report"
        ]
        if v not in valid_types:
            raise ValueError(f"Report type must be one of: {', '.join(valid_types)}")
        return v

    @validator('tone')
    def validate_tone(cls, v):
        valid_tones = [
            "objective",  # Impartial and unbiased presentation
            "formal",  # Academic standards with sophisticated language
            "analytical",  # Critical evaluation and examination
            "persuasive",  # Convincing viewpoint
            "informative",  # Clear and comprehensive information
            "explanatory",  # Clarifying complex concepts
            "descriptive",  # Detailed depiction
            "critical",  # Judging validity and relevance
            "comparative",  # Juxtaposing different theories
            "speculative",  # Exploring hypotheses
            "reflective",  # Personal insights
            "narrative",  # Story-based presentation
            "humorous",  # Light-hearted and engaging
            "optimistic",  # Highlighting positive aspects
            "pessimistic"  # Focusing on challenges
        ]
        if v not in valid_tones:
            raise ValueError(f"Tone must be one of: {', '.join(valid_tones)}")
        return v


class AuthRequest(BaseModel):
    """Model for authentication requests"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)