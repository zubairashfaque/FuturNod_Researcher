# Main application entry point
import logging
import uvicorn
import nest_asyncio
import ssl
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.config import API_CONFIG, LOGGING_CONFIG
from api.routes import router as api_router
from api.security import setup_security_middleware

# Enable nested asyncio for Jupyter-like environments
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG["level"]),
    format=LOGGING_CONFIG["format"]
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=API_CONFIG["title"],
    description=API_CONFIG["description"],
    version=API_CONFIG["version"],
    docs_url=API_CONFIG["docs_url"],
    redoc_url=API_CONFIG["redoc_url"]
)

# Setup security middleware
setup_security_middleware(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


# Exception handler for HTTP exceptions
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "FuturNod Researcher API",
        "version": API_CONFIG["version"],
        "status": "operational"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": API_CONFIG["version"]
    }


if __name__ == "__main__":
    # SSL context for HTTPS
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

    # Path to your SSL certificate and key files
    # You need to generate or obtain these files
    ssl_context.load_cert_chain(
        certfile="./certs/server.crt",
        keyfile="./certs/server.key"
    )

    # Run with SSL context for HTTPS
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,  # Standard HTTPS port is 443, but 8443 is common for development
        ssl_certfile="./certs/server.crt",
        ssl_keyfile="./certs/server.key",
        reload=True
    )