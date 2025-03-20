ROM python:3.10-slim

WORKDIR /app

# Install necessary system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies first to leverage Docker cache
COPY pyproject.toml README.md ./

# Add wheel build config to pyproject.toml
RUN echo '[tool.hatch.build.targets.wheel]\npackages = ["api", "core", "models"]' >> pyproject.toml

# Copy the rest of the application
COPY . .

# Create a directory for SSL certificates if it doesn't exist
RUN mkdir -p /app/certs

# Install dependencies including pytest for testing
RUN pip install --upgrade pip \
    && pip install uv \
    && uv pip install --system . \
    && pip install pytest pytest-asyncio pytest-cov

# Create a non-root user and switch to it
RUN useradd -m appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose both HTTP and HTTPS ports
#EXPOSE 8000
#EXPOSE 8383

# Use the SSL certificates for HTTPS
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8383", "--ssl-keyfile", "/app/certs/server.key", "--ssl-certfile", "/app/certs/server.crt"]
