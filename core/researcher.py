import logging
import uuid
import asyncio
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

import nest_asyncio
from gpt_researcher import GPTResearcher
from api.config import RESEARCHER_CONFIG
from api.security import validate_and_sanitize_input
from api.cache import cached
from core.storage import save_research_result

# Apply nest_asyncio for running in environments that already have an event loop
nest_asyncio.apply()

logger = logging.getLogger(__name__)


class Researcher:
    """Main researcher class for conducting AI-powered research"""

    @staticmethod
    async def _conduct_research(
            query: str,
            report_type: str
    ) -> Tuple[str, Dict[str, Any], float, List[str], List[Dict[str, Any]]]:
        """
        Conduct research using GPT-Researcher

        Args:
            query: Research query
            report_type: Type of report to generate

        Returns:
            Tuple of (report, research_context, costs, images, sources)
        """
        try:
            # Initialize GPT-Researcher
            # We need to validate that OPENAI_API_KEY is set in environment
            if not RESEARCHER_CONFIG.get("openai_api_key"):
                logger.error("OpenAI API key is not set")
                raise ValueError("OpenAI API key is not set")

            # Create the researcher instance
            researcher = GPTResearcher(query, report_type)

            # Conduct research
            research_result = await researcher.conduct_research()

            # Write report
            report = await researcher.write_report()

            # Get additional information
            research_context = researcher.get_research_context()
            research_costs = researcher.get_costs()
            research_images = researcher.get_research_images()
            research_sources = researcher.get_research_sources()

            return report, research_context, research_costs, research_images, research_sources

        except Exception as e:
            logger.error(f"Error conducting research: {str(e)}")
            raise

    @staticmethod
    @cached()  # Apply caching to optimize repeated research requests
    async def conduct_research(
            query: str,
            report_type: str = "research_report"
    ) -> Dict[str, Any]:
        """
        Conduct research and return results

        Args:
            query: Research query
            report_type: Type of report to generate

        Returns:
            Research results dictionary
        """
        # Validate and sanitize input
        sanitized_query = validate_and_sanitize_input(query)

        # Generate a unique ID for this research
        report_id = str(uuid.uuid4())

        # Conduct research
        logger.info(f"Starting research for query: {sanitized_query}")
        report, research_context, research_costs, research_images, research_sources = await Researcher._conduct_research(
            sanitized_query,
            report_type
        )

        # Prepare response data
        research_result = {
            "query": sanitized_query,
            "report_type": report_type,
            "report": report,
            "research_costs": research_costs,
            "research_images": research_images,
            "research_sources": research_sources,
            "completed_at": datetime.now().isoformat(),
            "report_id": report_id
        }

        # Save research result
        await save_research_result(research_result)

        return research_result