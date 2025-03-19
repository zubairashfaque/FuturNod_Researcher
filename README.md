Here's a complete README.md file for the FuturNod Researcher project:

```markdown
# FuturNod Researcher API

An AI-powered research API that uses GPT-Researcher and Tavily API to conduct comprehensive research on any topic. This service provides fast, accurate, and well-structured research reports for a variety of use cases.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Features

- **AI-Powered Research**: Leverages GPT-Researcher and Tavily API to conduct thorough research on any topic
- **Multiple Report Formats**: Supports various report types including research reports, executive summaries, bullet points, and more
- **Secure API**: Implements authentication, input sanitization, and secure communications
- **Performance Optimization**: Built-in caching system reduces redundant research and improves response times
- **Modular Architecture**: Clean separation of concerns for easy maintenance and extensibility
- **Docker Support**: Simple deployment using Docker and Docker Compose
- **HTTPS Support**: Secure communication using SSL/TLS
- **Comprehensive Testing**: Includes unit tests, integration tests, and end-to-end tests

## 📋 Prerequisites

Before you begin, ensure you have the following:

- **Python 3.10+** installed on your system
- **OpenAI API Key** (get one at [OpenAI Platform](https://platform.openai.com/))
- **Tavily API Key** (get one at [Tavily AI](https://tavily.com/))
- **Docker** (optional, for containerized deployment)

## 🔧 Installation

### Local Installation with uv

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/FuturNod_Researcher.git
   cd FuturNod_Researcher
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup_local.sh
   ./setup_local.sh
   ```

3. **Edit the `.env` file with your API keys**:
   ```ini
   OPENAI_API_KEY=your-openai-api-key
   TAVILY_API_KEY=your-tavily-api-key
   API_KEYS=your-api-key-for-authentication
   ```

4. **Activate the virtual environment and run the API**:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   python -m app.api
   ```

### Docker Installation

1. **Clone the repository and set up environment**:
   ```bash
   git clone https://github.com/yourusername/FuturNod_Researcher.git
   cd FuturNod_Researcher
   cp .env.sample .env
   # Edit the .env file with your API keys
   ```

2. **Build and run with Docker Compose**:
   ```bash
   docker-compose up -d
   ```

3. **Check the logs**:
   ```bash
   docker-compose logs -f
   ```

## 🔍 API Usage

### Research API Endpoint

**Endpoint**: `POST /research`

**Headers**:
- `X-API-Key`: Your API key
- `Content-Type`: application/json

**Request Body**:
```json
{
  "query": "What are the latest advancements in quantum computing?",
  "report_type": "research_report"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Research task started successfully. Check the status endpoint for results.",
  "request_id": "abc123def456",
  "data": {
    "task_status": "processing"
  }
}
```

### Status Endpoint

**Endpoint**: `GET /status/{request_id}`

**Headers**:
- `X-API-Key`: Your API key

**Response** (when task is complete):
```json
{
  "success": true,
  "message": "Research completed successfully",
  "request_id": "abc123def456",
  "data": {
    "file_output": "# Research Report: What are the latest advancements in quantum computing?...",
    "file_path": "results/research_abc123def456.md",
    "report": "...",
    "sources": [...],
    "costs": {...},
    "metadata": {...}
  }
}
```

### Health Check Endpoint

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2023-06-15T12:34:56.789Z"
}
```

### Available Report Types

| Type | Description |
|------|-------------|
| `research_report` | Comprehensive research report with detailed findings |
| `executive_summary` | Brief summary focused on key points for executives |
| `bullet_points` | Key findings in bullet point format for quick review |
| `blog_post` | Research formatted as a blog post for publishing |
| `investment_analysis` | Analysis focused on investment aspects and financial considerations |
| `market_analysis` | Analysis of market trends, competitors, and opportunities |
| `comparison` | Comparison-focused analysis between multiple options or technologies |
| `pros_and_cons` | List of advantages and disadvantages of the subject |
| `technical_deep_dive` | Detailed technical analysis for specialized audiences |

## 🧪 Testing

### Running Unit Tests

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_api.py
```

### Running End-to-End Test

```bash
# Run the end-to-end test with default settings
python e2e_test.py

# Run with custom settings
python e2e_test.py --url https://localhost:8000 --api-key your-api-key --query "What is quantum computing?" --report-type bullet_points
```

## 📁 Project Structure

```
FuturNod_Researcher/
├── Agents/                      # Agent module directory
│   └── src/
│       └── Researcher/
│           ├── __init__.py
│           └── agent.py         # Core research agent implementation
├── app/                         # API application directory
│   ├── __init__.py
│   ├── api.py                   # FastAPI implementation
│   ├── cache_manager.py         # Caching system for optimization
│   └── security_utils.py        # Security features and input sanitization
├── tests/                       # Test directory
│   ├── __init__.py
│   ├── test_api.py              # API integration tests
│   ├── test_cache.py            # Cache manager unit tests
│   └── test_security.py         # Security utilities unit tests
├── results/                     # Directory for research results
├── logs/                        # Log files directory
├── ssl_certs/                   # SSL certificates for HTTPS
├── .env                         # Environment variables (not in git)
├── .env.sample                  # Sample environment file
├── .gitignore                   # Git ignore file
├── docker-compose.yml           # Docker Compose configuration
├── Dockerfile                   # Docker configuration
├── e2e_test.py                  # End-to-end test script
├── pyproject.toml               # Python project configuration
├── README.md                    # This README file
└── setup_local.sh               # Local setup script
```

## 🔒 Security Considerations

- **API Key Authentication**: All requests require a valid API key
- **Input Sanitization**: Prevents injection attacks and harmful content
- **HTTPS Encryption**: All communication is encrypted with SSL/TLS
- **Content Validation**: Research queries are validated for safety

## ⚙️ Configuration Options

The API can be configured using environment variables in the `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Port to run the API on | 8000 |
| `API_KEYS` | Comma-separated list of valid API keys | (random generated) |
| `ALLOWED_ORIGINS` | CORS allowed origins | * |
| `OPENAI_API_KEY` | OpenAI API key | (required) |
| `TAVILY_API_KEY` | Tavily API key | (required) |
| `CACHE_ENABLED` | Enable/disable caching | true |
| `CACHE_TTL` | Cache time-to-live in seconds | 3600 |
| `LOG_LEVEL` | Logging level | INFO |

## 🔄 Performance Optimization

- **Caching**: Results are cached to avoid redundant research requests
- **Asynchronous Processing**: Research tasks run asynchronously for better concurrency
- **Resource Management**: Efficient handling of connections and resources
- **Structured Output**: Well-formatted results for easy processing

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔮 Future Enhancements

- **Enhanced Analytics**: Add detailed analytics for research requests
- **Advanced Caching**: Implement Redis-based distributed caching
- **Custom Research Parameters**: Allow more fine-grained control over the research process
- **Webhooks**: Support for webhook notifications when research is complete
- **Result Export**: Add support for exporting research in various formats (PDF, DOCX)
- **Admin Dashboard**: Web UI for monitoring and managing research tasks

## 🐛 Troubleshooting

### Common Issues

1. **SSL Certificate Issues**:
   - If you encounter "SSL: CERTIFICATE_VERIFY_FAILED" errors during testing, use the `--verify-ssl=false` flag with the e2e_test.py script
   - Regenerate certificates if needed using the setup script

2. **API Key Issues**:
   - Ensure your `.env` file has the API_KEYS variable set
   - Make sure you're using a valid API key in your requests
   - Check that the API key is being sent in the X-API-Key header

3. **Docker Issues**:
   - Ensure Docker and Docker Compose are installed and running
   - Check if port 8000 is already in use: `netstat -tuln | grep 8000`
   - Verify environment variables are correctly set in the container: `docker-compose exec futurnod-researcher env`

4. **Research API Issues**:
   - Check if the OpenAI and Tavily API keys are valid and have sufficient quota
   - Verify that the query is not being detected as harmful content
   - Check the logs for detailed error messages: `docker-compose logs -f` or `cat logs/api.log`

For more troubleshooting help, check the logs or open an issue on GitHub.
```

This comprehensive README provides all the necessary information about your FuturNod Researcher project, including:

1. Features and capabilities
2. Installation instructions for both local and Docker deployment
3. Detailed API documentation with examples
4. Testing procedures
5. Project structure overview
6. Security considerations
7. Configuration options
8. Performance optimizations
9. Troubleshooting guides
10. Future enhancement plans

The README is well-structured with clear sections, tables, and code examples to make it easy for users to understand and use your API.
