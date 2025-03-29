# FuturNod Researcher API

A modular, optimized, and secure API for AI-powered research using GPT-Researcher and Tavily API.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Environment Variables](#environment-variables)
- [Deployment](#deployment)
  - [Docker Deployment](#docker-deployment)
  - [SSL Configuration](#ssl-configuration)
- [API Usage](#api-usage)
  - [Authentication](#authentication)
  - [Conducting Research](#conducting-research)
  - [Retrieving Research Results](#retrieving-research-results)
  - [Deleting Research Results](#deleting-research-results)
- [Command Line Interface](#command-line-interface)
- [Development](#development)
  - [Running Tests](#running-tests)
  - [Code Structure](#code-structure)
- [Security Features](#security-features)
- [Caching](#caching)
- [License](#license)

## Overview

FuturNod Researcher API is a FastAPI-based application that provides a secure interface to AI-powered research capabilities. It leverages GPT-Researcher for conducting in-depth research on various topics and generating comprehensive reports with customizable tones and formats.

## Features

- **AI-Powered Research**: Utilize OpenAI and Tavily API to conduct comprehensive research on any topic
- **Multiple Report Types**: Generate various types of reports including detailed reports, research summaries, outlines, and more
- **Customizable Tone**: Select from 15 different tones for your research reports
- **Secure Authentication**: JWT-based authentication for securing API endpoints
- **Result Storage**: Automatic storage and retrieval of research results
- **API Caching**: Efficient caching to optimize repeated research requests
- **SSL Support**: Built-in HTTPS support with SSL certificate configuration
- **Docker Support**: Easy deployment with Docker and docker-compose
- **Command Line Interface**: User-friendly CLI for interacting with the API

## Project Structure

```
FuturNod_Researcher/
├── api/                    # API module
│   ├── __init__.py
│   ├── auth.py             # Authentication module
│   ├── cache.py            # Caching module
│   ├── config.py           # Configuration module
│   ├── routes.py           # API routes
│   ├── security.py         # Security middleware and utilities
│   └── utils.py            # Utility functions
├── certs/                  # SSL certificates
│   ├── server.crt
│   └── server.key
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── researcher.py       # Research implementation
│   └── storage.py          # Storage management
├── models/                 # Data models
│   ├── __init__.py
│   ├── request.py          # Request models
│   └── response.py         # Response models
├── results/                # Research results storage
├── scripts/                # Utility scripts
│   └── __init__.py
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py         # Test configuration
│   └── test_core.py        # Core tests
├── .env.example            # Environment variables example
├── .gitignore              # Git ignore file
├── cli.py                  # Command line interface
├── docker-compose.yml      # Docker Compose configuration
├── Dockerfile              # Docker configuration
├── main.py                 # Main application entry point
├── pyproject.toml          # Project metadata and dependencies
├── README.md               # This file
└── run_tests.sh            # Test runner script
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose (for containerized deployment)
- OpenAI API key
- Tavily API key

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/FuturNod_Researcher.git
   cd FuturNod_Researcher
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -e .
   ```

3. Copy the example environment file and edit it with your settings:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred text editor
   ```

### Environment Variables

Create a `.env` file with the following variables:

```
# API Configuration
SECRET_KEY=your-secret-key-here
SSL_ENABLED=true

# Authentication Configuration (for production)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-password
# Alternatively, use ADMIN_PASSWORD_HASH for pre-hashed password

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
```

## Deployment

### Docker Deployment

The easiest way to deploy FuturNod Researcher API is using Docker:

1. Make sure you have Docker and Docker Compose installed.
2. Create and configure your `.env` file as described above.
3. Run the deployment script:
   ```bash
   bash deploy_futurnod.sh
   ```

Or manually using Docker Compose:
   ```bash
   docker-compose up -d
   ```

4. The API will be available at `https://localhost:8383`

### SSL Configuration

The API uses HTTPS by default. SSL certificates are automatically generated during deployment if they don't exist:

- Self-signed certificates are created in the `certs/` directory
- For production, replace these with certificates from a trusted Certificate Authority
- Certificates should be named `server.crt` and `server.key` in the `certs/` directory

To disable SSL, set `SSL_ENABLED=false` in your `.env` file.

## API Usage

### Authentication

1. Get an access token:

```bash
curl -k -X POST https://localhost:8383/token \
  -d "username=admin&password=your-password" \
  -H "Content-Type: application/x-www-form-urlencoded"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_at": "2025-03-29T15:30:45.123456"
}
```

### Conducting Research

```bash
curl -k -X POST https://localhost:8383/research \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Latest advancements in AI technology",
    "report_type": "detailed_report",
    "tone": "analytical"
  }'
```

#### Available Report Types
- `research_report`: Summary - Short and fast (~2 min)
- `detailed_report`: Detailed - In depth and longer (~5 min)
- `resource_report`
- `outline_report`
- `custom_report`
- `subtopic_report`

#### Available Tones
- `objective`: Impartial and unbiased presentation
- `formal`: Academic standards with sophisticated language
- `analytical`: Critical evaluation and examination
- `persuasive`: Convincing viewpoint
- `informative`: Clear and comprehensive information
- `explanatory`: Clarifying complex concepts
- `descriptive`: Detailed depiction
- `critical`: Judging validity and relevance
- `comparative`: Juxtaposing different theories
- `speculative`: Exploring hypotheses
- `reflective`: Personal insights
- `narrative`: Story-based presentation
- `humorous`: Light-hearted and engaging
- `optimistic`: Highlighting positive aspects
- `pessimistic`: Focusing on challenges

### Retrieving Research Results

List all research reports:
```bash
curl -k -X GET https://localhost:8383/research?limit=10&offset=0 \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

Get a specific research report:
```bash
curl -k -X GET https://localhost:8383/research/REPORT_ID_HERE \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Deleting Research Results

```bash
curl -k -X DELETE https://localhost:8383/research/REPORT_ID_HERE \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Command Line Interface

The API includes a command-line interface for easy access:

```bash
python cli.py "What are the latest advancements in AI?" --report_type detailed_report --tone analytical
```

Required arguments:
- `query`: The research query (first positional argument)
- `--report_type`: Type of report to generate

Optional arguments:
- `--tone`: Tone of the report (defaults to "objective")

The CLI will save the research report as a Markdown file and display a snippet of the results.

## Development

### Running Tests

Run the tests using the provided script:

```bash
bash run_tests.sh
```

Or with coverage:

```bash
bash run_tests.sh --cov
```

### Code Structure

- **API Layer**: The `api/` directory contains the FastAPI routes, authentication, security, and caching mechanisms.
- **Core Layer**: The `core/` directory contains the core research functionality and storage management.
- **Models Layer**: The `models/` directory contains the Pydantic models for requests and responses.
- **Main Application**: The `main.py` file is the entry point for the FastAPI application.

## Security Features

The API includes several security features:

- **JWT Authentication**: Secure authentication using JSON Web Tokens
- **HTTPS Support**: SSL/TLS encryption for all API traffic
- **Input Validation**: Comprehensive input validation to prevent injection attacks
- **Security Headers**: Automatically adds security headers to responses
- **Content Security Policy**: Implements Content Security Policy headers
- **Prompt Injection Prevention**: Detection and prevention of prompt injection attacks

## Caching

The API supports two types of caching:

- **Memory Cache**: For single-instance deployments
- **Redis Cache**: For distributed deployments

Configure caching in the `.env` file:

```
CACHE_ENABLED=true
CACHE_TYPE=memory  # or redis
REDIS_URL=redis://localhost:6379/0  # required for redis cache
CACHE_TTL=3600  # Cache TTL in seconds
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.