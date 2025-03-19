#!/bin/bash

# Script to create the FuturNod Researcher API project structure
# Usage: bash create_project_structure.sh

set -e  # Exit on error

# Create base directory
echo "Creating FuturNod_Researcher project structure..."
mkdir -p FuturNod_Researcher
cd FuturNod_Researcher

# Create main directories
mkdir -p api core models tests results scripts

# Create __init__.py files
touch api/__init__.py
touch core/__init__.py
touch models/__init__.py
touch tests/__init__.py
touch scripts/__init__.py

# Create API module files
echo "# API configuration module" > api/config.py
echo "# API routes module" > api/routes.py
echo "# API security module" > api/security.py
echo "# API authentication module" > api/auth.py
echo "# API caching module" > api/cache.py
echo "# API utilities module" > api/utils.py

# Create core module files
echo "# Core researcher implementation" > core/researcher.py
echo "# Storage management module" > core/storage.py

# Create model files
echo "# Request data models" > models/request.py
echo "# Response data models" > models/response.py

# Create test files
echo "# Test configuration" > tests/conftest.py
echo "# API tests" > tests/test_api.py
echo "# Core functionality tests" > tests/test_core.py
echo "# Security tests" > tests/test_security.py
mkdir -p tests/sample_data

# Create script files
echo "# Setup and utility script" > scripts/setup.py
chmod +x scripts/setup.py

# Create main application files
echo "# Main application entry point" > main.py
touch pyproject.toml
touch Dockerfile
touch docker-compose.yml
touch .env.example
touch README.md
touch .gitignore

echo "# FuturNod Researcher API" > README.md
echo "A modular, optimized, and secure API for AI-powered research using GPT-Researcher and Tavily API." >> README.md

# Create a basic .gitignore
cat << EOF > .gitignore
# Python cache files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environment
venv/
env/
ENV/
.venv/
.uv/

# Environment variables
.env

# IDE files
.idea/
.vscode/
*.swp
*.swo

# Logs
logs/
*.log

# Test coverage
.coverage
htmlcov/
.pytest_cache/

# Research results
results/*.json

# Docker
.dockerignore

# Miscellaneous
.DS_Store
EOF

# Create basic pyproject.toml
cat << EOF > pyproject.toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "futurnod-researcher"
version = "1.0.0"
description = "Modular, optimized, and secure API for AI-powered research using GPT-Researcher and Tavily API"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "FuturNod Team", email = "info@futurnod.com"},
]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn>=0.23.2",
    "pydantic>=2.4.2",
    "python-dotenv>=1.0.0",
    "python-jose>=3.3.0",
    "passlib>=1.7.4",
    "bcrypt>=4.0.1",
    "cryptography>=41.0.4",
    "httpx>=0.25.0",
    "nest-asyncio>=1.5.8",
    "redis>=5.0.1",
    "gpt-researcher>=0.0.5",
    "tavily-python>=0.2.5",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.2",
    "pytest-asyncio>=0.21.1",
    "pytest-cov>=4.1.0",
    "black>=23.9.1",
    "isort>=5.12.0",
    "mypy>=1.5.1",
    "ruff>=0.1.0",
]
EOF

# Create basic Dockerfile
cat << EOF > Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=off \\
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Install system dependencies
RUN apt-get update \\
    && apt-get install -y --no-install-recommends gcc python3-dev \\
    && apt-get clean \\
    && rm -rf /var/lib/apt/lists/*

# Install UV and project dependencies
COPY pyproject.toml .
RUN pip install --upgrade pip \\
    && pip install uv \\
    && uv pip install --system -e .

# Copy project files
COPY . .

# Create results directory
RUN mkdir -p results

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create basic docker-compose.yml
cat << EOF > docker-compose.yml
version: '3.8'

services:
  api:
    container_name: futurnod-researcher-api
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./results:/app/results
    env_file:
      - .env
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  redis:
    container_name: futurnod-researcher-redis
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
EOF

# Create basic .env.example
cat << EOF > .env.example
# API Configuration
SECRET_KEY=your-secret-key-here
SSL_ENABLED=false

# GPT-Researcher Configuration
OPENAI_API_KEY=your-openai-api-key-here
TAVILY_API_KEY=your-tavily-api-key-here

# Cache Configuration
CACHE_ENABLED=true
CACHE_TYPE=memory  # memory or redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600  # Cache TTL in seconds (1 hour)

# Logging Configuration
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
EOF

echo "Project structure created successfully!"
echo "Navigate to the project directory: cd FuturNod_Researcher"

# Return to original directory
cd ..