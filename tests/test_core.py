# Core functionality tests
import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from core.researcher import Researcher
from core.storage import save_research_result, get_research_result, list_research_results, delete_research_result
from api.config import RESULTS_DIR


@pytest.mark.asyncio
async def test_researcher_conduct_research():
    """Test the research conducting functionality"""
    # Create mock GPTResearcher class and methods
    mock_gpt_researcher = MagicMock()
    mock_gpt_researcher.conduct_research = AsyncMock(return_value={})
    mock_gpt_researcher.write_report = AsyncMock(return_value="Test research report")
    mock_gpt_researcher.get_research_context = MagicMock(return_value={})
    mock_gpt_researcher.get_costs = MagicMock(return_value=0.123)
    mock_gpt_researcher.get_research_images = MagicMock(return_value=["image1.jpg"])
    mock_gpt_researcher.get_research_sources = MagicMock(return_value=[{"url": "example.com"}])

    # Patch the GPTResearcher class
    with patch("core.researcher.GPTResearcher", return_value=mock_gpt_researcher), \
            patch("core.storage.save_research_result", new_callable=AsyncMock) as mock_save:
        # Set environment variables for testing
        os.environ["OPENAI_API_KEY"] = "test-key"

        # Call the conduct_research method
        result = await Researcher.conduct_research("Test query", "research_report")

        # Verify the result
        assert result["query"] == "Test query"
        assert result["report_type"] == "research_report"
        assert result["report"] == "Test research report"
        assert result["research_costs"] == 0.123
        assert result["research_images"] == ["image1.jpg"]
        assert result["research_sources"] == [{"url": "example.com"}]
        assert "completed_at" in result
        assert "report_id" in result

        # Verify that save_research_result was called
        mock_save.assert_called_once()

        # Clean up
        os.environ.pop("OPENAI_API_KEY", None)


@pytest.mark.asyncio
async def test_save_research_result(tmp_path):
    """Test saving research results to file"""
    # Set up a temporary results directory
    original_results_dir = RESULTS_DIR
    test_results_dir = tmp_path / "results"
    test_results_dir.mkdir()

    # Patch the RESULTS_DIR
    with patch("core.storage.RESULTS_DIR", test_results_dir):
        # Test data
        test_data = {
            "query": "Test query",
            "report_type": "research_report",
            "report": "Test report content",
            "research_costs": 0.123,
            "research_images": ["image1.jpg"],
            "research_sources": [{"url": "example.com"}],
            "completed_at": "2025-03-20T12:00:00",
            "report_id": "test-report-id"
        }

        # Save the research result
        file_path = await save_research_result(test_data)

        # Verify that the file exists
        assert Path(file_path).exists()

        # Verify the file contents
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            assert saved_data == test_data


@pytest.mark.asyncio
async def test_get_research_result(tmp_path):
    """Test retrieving research results from file"""
    # Set up a temporary results directory
    test_results_dir = tmp_path / "results"
    test_results_dir.mkdir()

    # Patch the RESULTS_DIR
    with patch("core.storage.RESULTS_DIR", test_results_dir):
        # Test data
        test_data = {
            "query": "Test query",
            "report_type": "research_report",
            "report": "Test report content",
            "research_costs": 0.123,
            "research_images": ["image1.jpg"],
            "research_sources": [{"url": "example.com"}],
            "completed_at": "2025-03-20T12:00:00",
            "report_id": "test-report-id"
        }

        # Save the research result to a file
        file_path = test_results_dir / "test_file.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Retrieve the research result
        result = await get_research_result("test-report-id")

        # Verify the result
        assert result == test_data

        # Test retrieving a non-existent report
        result = await get_research_result("non-existent-id")
        assert result is None


@pytest.mark.asyncio
async def test_list_research_results(tmp_path):
    """Test listing research results"""
    # Set up a temporary results directory
    test_results_dir = tmp_path / "results"
    test_results_dir.mkdir()

    # Patch the RESULTS_DIR
    with patch("core.storage.RESULTS_DIR", test_results_dir):
        # Create test files
        test_data_1 = {
            "query": "Test query 1",
            "report_id": "test-report-id-1"
        }
        test_data_2 = {
            "query": "Test query 2",
            "report_id": "test-report-id-2"
        }

        # Save the test files
        file_path_1 = test_results_dir / "test_file_1.json"
        file_path_2 = test_results_dir / "test_file_2.json"

        with open(file_path_1, 'w', encoding='utf-8') as f:
            json.dump(test_data_1, f)

        with open(file_path_2, 'w', encoding='utf-8') as f:
            json.dump(test_data_2, f)

        # List the research results
        results = await list_research_results()

        # Verify the results
        assert len(results) == 2
        assert test_data_1 in results
        assert test_data_2 in results

        # Test pagination
        results = await list_research_results(limit=1, offset=0)
        assert len(results) == 1

        results = await list_research_results(limit=1, offset=1)
        assert len(results) == 1


@pytest.mark.asyncio
async def test_delete_research_result(tmp_path):
    """Test deleting research results"""
    # Set up a temporary results directory
    test_results_dir = tmp_path / "results"
    test_results_dir.mkdir()

    # Patch the RESULTS_DIR
    with patch("core.storage.RESULTS_DIR", test_results_dir):
        # Test data
        test_data = {
            "query": "Test query",
            "report_type": "research_report",
            "report": "Test report content",
            "research_costs": 0.123,
            "research_images": ["image1.jpg"],
            "research_sources": [{"url": "example.com"}],
            "completed_at": "2025-03-20T12:00:00",
            "report_id": "test-report-id"
        }

        # Save the research result to a file
        file_path = test_results_dir / "test_file.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)

        # Delete the research result
        result = await delete_research_result("test-report-id")

        # Verify the result
        assert result is True
        assert not file_path.exists()

        # Test deleting a non-existent report
        result = await delete_research_result("non-existent-id")
        assert result is False