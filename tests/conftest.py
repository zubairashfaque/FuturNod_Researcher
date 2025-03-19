# Test configuration
import pytest
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

# This is to make tests bypass authentication
@pytest.fixture(autouse=True)
def mock_auth_dependency():
    """Bypass authentication for tests by mocking the dependency"""
    with patch('api.routes.get_current_user') as mock_auth:
        # Return a mock user
        mock_auth.return_value = {"username": "testuser", "disabled": False}
        yield mock_auth


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    with TestClient(app) as client:
        yield client


@pytest.fixture
def auth_headers():
    """
    Get authentication headers for testing protected endpoints
    """
    # This is a mock token for testing purposes only
    # In a real test, we would get a real token from the /token endpoint
    mock_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.8JRkxmeBJLJSZ1GWMNLDPrj1MvjK0XA7h7Bxfvkw4AQ"

    return {"Authorization": f"Bearer {mock_token}"}


@pytest.fixture
def mock_research_request():
    """
    Get a mock research request for testing
    """
    return {
        "query": "Should I invest in Nvidia?",
        "report_type": "research_report"
    }


@pytest.fixture
def mock_research_response():
    """
    Get a mock research response for testing
    """
    return {
        "query": "Should I invest in Nvidia?",
        "report_type": "research_report",
        "report": "Mock research report content",
        "research_costs": 0.12345,
        "research_images": ["https://example.com/image1.jpg"],
        "research_sources": [{"url": "https://example.com/source1"}],
        "completed_at": "2025-03-20T12:00:00",
        "report_id": "test-report-id"
    }