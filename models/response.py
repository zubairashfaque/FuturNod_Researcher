# Response data models
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime


class ResearchResponse(BaseModel):
    """Model for research response data"""
    query: str = Field(..., description="Original research query")
    report_type: str = Field(..., description="Type of report generated")
    report: str = Field(..., description="Research report content")
    research_costs: float = Field(..., description="Cost of conducting the research")
    #research_images: Optional[List[str]] = Field(None, description="List of research images")
    #research_sources: Optional[List[dict]] = Field(None, description="List of research sources")
    completed_at: datetime = Field(default_factory=datetime.now, description="When the research was completed")
    report_id: str = Field(..., description="Unique ID for the research report")


class ErrorResponse(BaseModel):
    """Model for error responses"""
    detail: str = Field(..., description="Error detail message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="When the error occurred")


class TokenResponse(BaseModel):
    """Model for authentication token responses"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_at: datetime = Field(..., description="Token expiration time")


class StatusResponse(BaseModel):
    """Model for status responses"""
    status: str = Field(..., description="Status of the operation")
    message: str = Field(..., description="Status message")