#!/usr/bin/env python
import os
import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the API app
from app.api import app

# Create test client
client = TestClient(app)

# Get a valid API key for testing
API_KEY = os.getenv("API_KEYS", "test-key").split(",")[0]

class TestResearcherAPI:
    """Integration tests for the Researcher API."""
    
    def setup_method(self):
        """Set up each test method."""
        self.headers = {"X-API-Key": API_KEY}
    
    def test_health_endpoint(self):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
    
    def test_research_endpoint_validation(self):
        """Test validation in the research endpoint."""
        # Test without API key
        response = client.post("/research", json={"query": "Test query"})
        assert response.status_code == 401
        
        # Test with invalid API key
        response = client.post(
            "/research", 
            json={"query": "Test query"}, 
            headers={"X-API-Key": "invalid-key"}
        )
        assert response.status_code == 401
        
        # Test with empty query
        response = client.post(
            "/research", 
            json={"query": ""}, 
            headers=self.headers
        )
        assert response.status_code == 422  # Validation error
        
        # Test with invalid report type (should accept but use default)
        response = client.post(
            "/research", 
            json={"query": "Test query", "report_type": "invalid_type"}, 
            headers=self.headers
        )
        assert response.status_code == 200
    
    def test_research_endpoint_successful_request(self):
        """Test a successful research request."""
        # This is a mock test since we don't want to actually run the research
        # In a real test, you might want to mock the ResearcherAgent
        response = client.post(
            "/research", 
            json={"query": "What is artificial intelligence?", "report_type": "bullet_points"}, 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "task_status" in data["data"]
        assert data["data"]["task_status"] == "processing"
    
    def test_status_endpoint_nonexistent_task(self):
        """Test status endpoint for a non-existent task."""
        response = client.get(
            "/status/nonexistent-task-id", 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "not found" in data["message"].lower()
    
    def test_tasks_endpoint(self):
        """Test the tasks endpoint."""
        response = client.get(
            "/tasks", 
            headers=self.headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "active_tasks" in data["data"]
