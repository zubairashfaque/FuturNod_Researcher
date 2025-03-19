#!/usr/bin/env python
import os
import secrets
import logging
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join("logs", "api.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("futurnod_researcher")

# Create necessary directories
os.makedirs("logs", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Import local modules
from app.security_utils import verify_api_key, sanitizer
from Agents.src.Researcher.agent import ResearcherAgent

# Request model for Researcher API
class ResearcherRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The research query")
    report_type: str = Field("research_report", description="Type of report to generate")

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What are the latest developments in AI?",
                "report_type": "research_report"
            }
        }
    }

# API response model
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    request_id: str

# Track active tasks
active_tasks = {}

# Initialize FastAPI
app = FastAPI(
    title="FuturNod Researcher API",
    description="API for conducting AI-powered research using GPT-Researcher",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request ID and security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    request_id = secrets.token_hex(8)
    request.state.request_id = request_id

    # Process the request
    response = await call_next(request)

    # Add security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    response.headers["X-Request-ID"] = request_id
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

    return response

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", "unknown")
        }
    )

# Helper function to run research tasks
async def run_research_task(agent: ResearcherAgent, inputs: Dict[str, Any], request_id: str):
    try:
        logger.info(f"Starting research task for request {request_id}")
        
        # Run the research
        result = await agent.run_research(inputs, request_id)
        
        logger.info(f"Research task completed for request {request_id}")
        return result
    except Exception as e:
        logger.error(f"Error in research task for request {request_id}: {str(e)}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        # Clean up
        if request_id in active_tasks:
            del active_tasks[request_id]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Researcher API endpoint
@app.post("/research", response_model=ApiResponse)
async def research(
    request: Request,
    data: ResearcherRequest,
    api_key: str = Depends(verify_api_key)
):
    request_id = request.state.request_id
    logger.info(f"Request {request_id}: Research request received")

    # Sanitize inputs
    sanitized_data = sanitizer.sanitize_input(data.model_dump())

    try:
        # Create agent instance
        agent = ResearcherAgent()
        
        # Add request_id to inputs
        sanitized_data["request_id"] = request_id
        
        # Create and track task
        task = asyncio.create_task(run_research_task(agent, sanitized_data, request_id))
        active_tasks[request_id] = task
        
        # Return immediate response
        return ApiResponse(
            success=True,
            message="Research task started successfully. Check the status endpoint for results.",
            request_id=request_id,
            data={"task_status": "processing"}
        )
    except Exception as e:
        logger.error(f"Error starting research task: {str(e)}", exc_info=True)
        return ApiResponse(
            success=False,
            message=f"Failed to start research task: {str(e)}",
            request_id=request_id
        )

# Status check endpoint
@app.get("/status/{request_id}", response_model=ApiResponse)
async def get_status(
    request: Request,
    request_id: str,
    api_key: str = Depends(verify_api_key)
):
    logger.info(f"Checking status for request {request_id}")

    # Check if task is still running
    if request_id in active_tasks:
        task = active_tasks[request_id]
        
        if task.done():
            try:
                result = task.result()
                if result["success"]:
                    return ApiResponse(
                        success=True,
                        message="Research completed successfully",
                        data=result["result"],
                        request_id=request_id
                    )
                else:
                    return ApiResponse(
                        success=False,
                        message=f"Research failed: {result.get('error', 'Unknown error')}",
                        request_id=request_id
                    )
            except Exception as e:
                logger.error(f"Error retrieving task result: {str(e)}", exc_info=True)
                return ApiResponse(
                    success=False,
                    message=f"Error retrieving task result: {str(e)}",
                    request_id=request_id
                )
        else:
            return ApiResponse(
                success=True,
                message="Research is still in progress",
                data={"task_status": "processing"},
                request_id=request_id
            )
    
    # If not in active tasks, check for result files
    result_file = os.path.join("results", f"research_{request_id}.md")
    if os.path.exists(result_file):
        try:
            with open(result_file, "r") as f:
                content = f.read()
            
            # Also try to get the JSON result if available
            json_result = {}
            json_file = os.path.join("results", f"research_{request_id}", "result.json")
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    json_result = json.load(f)
            
            return ApiResponse(
                success=True,
                message="Research completed successfully",
                data={
                    "file_output": content,
                    "file_path": result_file,
                    **json_result
                },
                request_id=request_id
            )
        except Exception as e:
            logger.error(f"Error reading result file: {str(e)}", exc_info=True)
    
    # Check for error files
    error_file = os.path.join("results", f"research_{request_id}", "error.json")
    if os.path.exists(error_file):
        try:
            with open(error_file, "r") as f:
                error_data = json.load(f)
            
            return ApiResponse(
                success=False,
                message=f"Research failed: {error_data.get('error', 'Unknown error')}",
                request_id=request_id
            )
        except Exception as e:
            logger.error(f"Error reading error file: {str(e)}", exc_info=True)
    
    # If we get here, the task doesn't exist
    return ApiResponse(
        success=False,
        message="Research task not found",
        request_id=request_id
    )

# Endpoint to list active research tasks
@app.get("/tasks", response_model=ApiResponse)
async def list_tasks(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    request_id = request.state.request_id
    
    # Get information about active tasks
    task_info = {}
    for task_id, task in active_tasks.items():
        task_info[task_id] = {
            "done": task.done(),
            "cancelled": task.cancelled(),
            "exception": str(task.exception()) if task.done() and task.exception() else None
        }
    
    return ApiResponse(
        success=True,
        message=f"Active tasks: {len(active_tasks)}",
        data={"active_tasks": task_info},
        request_id=request_id
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    
    # Get SSL cert paths
    ssl_dir = "ssl_certs"
    certfile = os.path.join(ssl_dir, "server.crt")
    keyfile = os.path.join(ssl_dir, "server.key")
    
    # Check if SSL certs exist
    if not os.path.exists(certfile) or not os.path.exists(keyfile):
        logger.error(f"SSL certificate files not found at {certfile} and {keyfile}")
        raise FileNotFoundError("SSL certificate files not found")
    
    # Start the server
    logger.info(f"Starting server on port {port}")
    uvicorn.run(
        "app.api:app",
        host="0.0.0.0",
        port=port,
        ssl_certfile=certfile,
        ssl_keyfile=keyfile
    )
