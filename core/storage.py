# Storage management module
import os
import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from api.config import RESULTS_DIR

logger = logging.getLogger(__name__)


async def save_research_result(result: Dict[str, Any]) -> str:
    """
    Save research result to the results directory

    Args:
        result: Research result dictionary

    Returns:
        Path to the saved file
    """
    # Create results directory if it doesn't exist
    if not RESULTS_DIR.exists():
        RESULTS_DIR.mkdir(parents=True)

    # Generate filename based on report_id and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_id = result.get("report_id", "unknown")
    filename = f"{timestamp}_{report_id}.json"

    # Create full path
    file_path = RESULTS_DIR / filename

    # Save to file as JSON
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved research result to {file_path}")

    return str(file_path)


async def get_research_result(report_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a research result by ID

    Args:
        report_id: ID of the research report

    Returns:
        Research result dictionary or None if not found
    """
    # Check if results directory exists
    if not RESULTS_DIR.exists():
        return None

    # Find file with matching report_id
    for file_path in RESULTS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("report_id") == report_id:
                    return data
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")

    # Not found
    return None


async def list_research_results(limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
    """
    List research results with pagination

    Args:
        limit: Maximum number of results to return
        offset: Offset for pagination

    Returns:
        List of research results
    """
    # Check if results directory exists
    if not RESULTS_DIR.exists():
        return []

    # Get all JSON files in the results directory
    files = sorted(RESULTS_DIR.glob("*.json"), key=os.path.getmtime, reverse=True)

    # Apply pagination
    paginated_files = files[offset:offset + limit]

    # Load research results
    results = []
    for file_path in paginated_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                results.append(data)
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {str(e)}")

    return results


async def delete_research_result(report_id: str) -> bool:
    """
    Delete a research result by ID

    Args:
        report_id: ID of the research report

    Returns:
        True if deleted successfully, False otherwise
    """
    # Check if results directory exists
    if not RESULTS_DIR.exists():
        return False

    # Find file with matching report_id
    for file_path in RESULTS_DIR.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("report_id") == report_id:
                    # Delete the file
                    file_path.unlink()
                    logger.info(f"Deleted research result {report_id}")
                    return True
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")

    # Not found
    return False