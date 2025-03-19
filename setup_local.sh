#!/bin/bash
# setup_local.sh

# Create necessary directories
mkdir -p Agents/src/Researcher
mkdir -p app
mkdir -p tests
mkdir -p results
mkdir -p logs
mkdir -p ssl_certs

# Install uv if not installed
if ! command -v uv &> /dev/null; then
    echo "Installing uv package manager..."
    pip install uv
fi

# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies using uv
uv pip install -e ".[dev]"

# Generate SSL certificates for local development
if [ ! -f "ssl_certs/server.crt" ] || [ ! -f "ssl_certs/server.key" ]; then
    echo "Generating SSL certificates..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout ssl_certs/server.key -out ssl_certs/server.crt \
        -subj "/CN=localhost" \
        -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.sample .env
    echo "Created .env file. Please update it with your API keys."
fi

echo "Local development environment setup complete!"
echo "Don't forget to:"
echo "1. Update your .env file with your OpenAI and Tavily API keys"
echo "2. Activate the virtual environment: source .venv/bin/activate"
