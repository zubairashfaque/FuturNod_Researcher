FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy pyproject.toml
COPY pyproject.toml .

# Install dependencies
RUN uv pip install .

# Copy application code
COPY . .

# Create directories if they don't exist
RUN mkdir -p results logs ssl_certs

# Generate SSL certificates if they don't exist
RUN if [ ! -f "ssl_certs/server.crt" ] || [ ! -f "ssl_certs/server.key" ]; then \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl_certs/server.key -out ssl_certs/server.crt \
    -subj "/CN=localhost" \
    -addext "subjectAltName = DNS:localhost,IP:127.0.0.1"; \
    fi

# Create non-root user for security
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "ssl_certs/server.key", "--ssl-certfile", "ssl_certs/server.crt"]
