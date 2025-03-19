#!/usr/bin/env python
import os
import json
import logging
import asyncio
import time
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

# Configure logging
logger = logging.getLogger("researcher_agent")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Try importing the cache manager and security utils
try:
    from app.cache_manager import cache
    from app.security_utils import sanitizer
    
    logger.info("Successfully imported cache and security utilities")
except ImportError:
    logger.warning("Cache or security utilities not found, using defaults")
    
    # Fallback implementations
    class DummyCache:
        def get(self, data):
            return None
        
        def set(self, data, result):
            pass
    
    class DummySanitizer:
        @staticmethod
        def sanitize_input(data):
            return data
        
        @staticmethod
        def validate_query(query):
            return bool(query)
        
        @staticmethod
        def validate_report_type(report_type):
            return True
    
    cache = DummyCache()
    sanitizer = DummySanitizer()

class ResearcherAgent:
    """
    Agent for conducting AI-powered research using GPT-Researcher and Tavily API.
    """
    
    def __init__(self):
        # Ensure the API keys are set
        required_keys = ['OPENAI_API_KEY', 'TAVILY_API_KEY']
        for key in required_keys:
            if not os.environ.get(key):
                logger.warning(f"Environment variable {key} is not set!")
        
        # Create results directory if it doesn't exist
        self.results_dir = os.path.join(os.getcwd(), "results")
        os.makedirs(self.results_dir, exist_ok=True)

    async def run_research(self, inputs: Dict[str, Any], request_id: str) -> Dict[str, Any]:
        """
        Run the research process using GPT-Researcher.
        
        Args:
            inputs: Dictionary containing 'query' and 'report_type'
            request_id: Unique identifier for this research request
            
        Returns:
            Dictionary with research results
        """
        try:
            # Sanitize inputs
            sanitized_inputs = sanitizer.sanitize_input(inputs)
            query = sanitized_inputs.get("query")
            report_type = sanitized_inputs.get("report_type", "research_report")
            
            # Validate inputs
            if not query:
                return {
                    "success": False,
                    "error": "Query is required"
                }
            
            if not sanitizer.validate_query(query):
                return {
                    "success": False,
                    "error": "Invalid query - contains potentially harmful content"
                }
            
            if not sanitizer.validate_report_type(report_type):
                logger.warning(f"Invalid report_type ({report_type}), defaulting to 'research_report'")
                report_type = "research_report"
            
            # Check cache first
            cache_key_data = {"query": query, "report_type": report_type}
            cache_key = self._generate_cache_key(cache_key_data)
            logger.info(f"Cache key for request {request_id}: {cache_key}")
            
            cached_result = cache.get(cache_key_data)
            
            if cached_result:
                logger.info(f"Using cached result for query: {query}")
                self._save_results(cached_result, request_id)
                return {
                    "success": True,
                    "result": cached_result,
                    "cached": True
                }
            
            # Import here to allow for potential lazy-loading
            try:
                from gpt_researcher import GPTResearcher
                import nest_asyncio
                
                # Apply nest_asyncio to allow nested event loops
                try:
                    nest_asyncio.apply()
                except RuntimeError:
                    logger.warning("nest_asyncio already applied or cannot be applied")
            except ImportError as e:
                logger.error(f"Error importing required modules: {str(e)}")
                return {
                    "success": False,
                    "error": f"Required module not found: {str(e)}"
                }
            
            logger.info(f"Starting research for query: {query}, report_type: {report_type}")
            
            # Record start time for performance tracking
            start_time = time.time()
            
            # Initialize the researcher
            researcher = GPTResearcher(query, report_type)
            
            # Conduct the research
            logger.info("Conducting research...")
            research_result = await researcher.conduct_research()
            
            # Write the report
            logger.info("Writing report...")
            report = await researcher.write_report()
            
            # Get additional information
            research_context = researcher.get_research_context()
            research_costs = researcher.get_costs()
            research_images = researcher.get_research_images()
            research_sources = researcher.get_research_sources()
            
            # Calculate execution time
            execution_time = time.time() - start_time
            logger.info(f"Research completed in {execution_time:.2f} seconds")
            
            # Create a comprehensive result dictionary
            result = {
                "report": report,
                "context": research_context,
                "costs": research_costs,
                "images": research_images,
                "sources": research_sources,
                "metadata": {
                    "query": query,
                    "report_type": report_type,
                    "execution_time": execution_time,
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
            
            # Save to cache for future use
            cache.set(cache_key_data, result)
            logger.info(f"Saved result to cache with key: {cache_key}")
            
            # Save results to files
            self._save_results(result, request_id)
            
            return {
                "success": True,
                "result": result,
                "cached": False
            }
            
        except Exception as e:
            logger.error(f"Error in research process: {str(e)}", exc_info=True)
            
            # Create error result for saving
            error_result = {
                "error": str(e),
                "metadata": {
                    "query": inputs.get("query", ""),
                    "report_type": inputs.get("report_type", "research_report"),
                    "timestamp": datetime.now().isoformat(),
                    "request_id": request_id
                }
            }
            
            # Save error information
            self._save_error(error_result, request_id)
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_cache_key(self, data: Dict[str, Any]) -> str:
        """
        Generate a cache key from input data.
        
        Args:
            data: Input data dictionary
            
        Returns:
            Cache key string
        """
        # Sort keys for consistent hash generation
        serialized = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.md5(serialized).hexdigest()
    
    def _save_results(self, result: Dict[str, Any], request_id: str) -> None:
        """
        Save research results to files.
        
        Args:
            result: Research results dictionary
            request_id: Unique identifier for this research request
        """
        try:
            # Create a directory for this specific research
            research_dir = os.path.join(self.results_dir, f"research_{request_id}")
            os.makedirs(research_dir, exist_ok=True)
            
            # Save the complete result as JSON
            with open(os.path.join(research_dir, "result.json"), "w") as f:
                json.dump(result, f, indent=2)
            
            # Save the report as markdown
            with open(os.path.join(research_dir, "report.md"), "w") as f:
                f.write(result["report"])
            
            # Save the sources as JSON
            with open(os.path.join(research_dir, "sources.json"), "w") as f:
                json.dump(result["sources"], f, indent=2)
                
            # Create a single file with all important information
            combined_file_path = os.path.join(self.results_dir, f"research_{request_id}.md")
            with open(combined_file_path, "w") as f:
                # Get query from metadata if available
                query = result.get("metadata", {}).get("query", "Unknown Query")
                report_type = result.get("metadata", {}).get("report_type", "research_report")
                
                f.write(f"# Research Report: {query}\n\n")
                f.write(f"**Report Type:** {report_type}\n")
                f.write(f"**Request ID:** {request_id}\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(result["report"])
                f.write("\n\n## Sources\n\n")
                for idx, source in enumerate(result["sources"], 1):
                    f.write(f"{idx}. [{source.get('title', 'Unknown Title')}]({source.get('url', '#')})\n")
                f.write("\n\n## Costs\n\n")
                total_cost = result.get('costs', {}).get('total_cost', 'N/A')
                if isinstance(total_cost, (int, float)):
                    f.write(f"Total Cost: ${total_cost:.4f}\n")
                else:
                    f.write(f"Total Cost: {total_cost}\n")
            
            logger.info(f"Saved research results to {research_dir} and {combined_file_path}")
            
        except Exception as e:
            logger.error(f"Error saving research results: {str(e)}", exc_info=True)
    
    def _save_error(self, error_result: Dict[str, Any], request_id: str) -> None:
        """
        Save error information to files.
        
        Args:
            error_result: Error information dictionary
            request_id: Unique identifier for this research request
        """
        try:
            # Create a directory for this specific research
            research_dir = os.path.join(self.results_dir, f"research_{request_id}")
            os.makedirs(research_dir, exist_ok=True)
            
            # Save the error information as JSON
            with open(os.path.join(research_dir, "error.json"), "w") as f:
                json.dump(error_result, f, indent=2)
            
            # Create a markdown file with error information
            combined_file_path = os.path.join(self.results_dir, f"research_{request_id}.md")
            with open(combined_file_path, "w") as f:
                query = error_result.get("metadata", {}).get("query", "Unknown Query")
                f.write(f"# Research Error: {query}\n\n")
                f.write(f"**Request ID:** {request_id}\n")
                f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("---\n\n")
                f.write(f"## Error\n\n{error_result['error']}\n\n")
                f.write("The research process encountered an error. Please try again later or with a different query.\n")
            
            logger.info(f"Saved error information to {research_dir} and {combined_file_path}")
            
        except Exception as e:
            logger.error(f"Error saving error information: {str(e)}", exc_info=True)

    def crew(self):
        """
        Returns a crew-compatible interface for consistency with other agents.
        """
        class MockCrew:
            def __init__(self, agent):
                self.agent = agent
                
            async def kickoff_async(self, inputs):
                request_id = inputs.get("request_id", datetime.now().strftime("%Y%m%d%H%M%S"))
                result = await self.agent.run_research(inputs, request_id)
                if result["success"]:
                    return result["result"]
                else:
                    raise Exception(result.get("error", "Unknown error in research process"))
                
            def kickoff(self, inputs):
                # Run the async method in a new event loop for compatibility
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(self.kickoff_async(inputs))
                finally:
                    loop.close()
        
        return MockCrew(self)
    
    def get_supported_report_types(self) -> List[Dict[str, str]]:
        """
        Get a list of supported report types with descriptions.
        
        Returns:
            List of dictionaries with report type and description
        """
        return [
            {"type": "research_report", "description": "Comprehensive research report with detailed findings"},
            {"type": "executive_summary", "description": "Brief summary focused on key points for executives"},
            {"type": "bullet_points", "description": "Key findings in bullet point format for quick review"},
            {"type": "blog_post", "description": "Research formatted as a blog post for publishing"},
            {"type": "investment_analysis", "description": "Analysis focused on investment aspects and financial considerations"},
            {"type": "market_analysis", "description": "Analysis of market trends, competitors, and opportunities"},
            {"type": "comparison", "description": "Comparison-focused analysis between multiple options or technologies"},
            {"type": "pros_and_cons", "description": "List of advantages and disadvantages of the subject"},
            {"type": "technical_deep_dive", "description": "Detailed technical analysis for specialized audiences"}
        ]

# For testing
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    async def test():
        agent = ResearcherAgent()
        result = await agent.run_research({
            "query": "What are the latest developments in AI?",
            "report_type": "research_report"
        }, "test_request_id")
        print(json.dumps(result, indent=2))
    
    # Set environment variables for testing
    if not os.environ.get("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. Testing may fail.")
    if not os.environ.get("TAVILY_API_KEY"):
        print("Warning: TAVILY_API_KEY not set. Testing may fail.")
    
    # Run the test
    asyncio.run(test())
