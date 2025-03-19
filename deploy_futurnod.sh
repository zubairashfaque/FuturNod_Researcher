#!/bin/bash

# Define the container name
CONTAINER_NAME="futurnod-researcher-api"

# Stop the Docker container if it is running
echo "Stopping Docker container: $CONTAINER_NAME..."
docker stop $CONTAINER_NAME

echo "Removing Docker container: $CONTAINER_NAME..."
docker rm $CONTAINER_NAME

# Ensure certificates directory exists
echo "Ensuring SSL certificates are present..."
mkdir -p ./certs

# Check if certificates exist, if not generate them
if [ ! -f "./certs/server.crt" ] || [ ! -f "./certs/server.key" ]; then
    echo "Generating self-signed SSL certificates..."

    # Generate a private key
    openssl genrsa -out ./certs/server.key 2048

    # Generate a CSR (Certificate Signing Request)
    openssl req -new -key ./certs/server.key -out ./certs/server.csr -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

    # Generate a self-signed certificate (valid for 365 days)
    openssl x509 -req -days 365 -in ./certs/server.csr -signkey ./certs/server.key -out ./certs/server.crt

    # Remove the CSR as it's no longer needed
    rm ./certs/server.csr

    echo "Self-signed SSL certificates have been generated in the ./certs directory."
    echo "Note: These are self-signed certificates suitable for development only."
    echo "For production, obtain certificates from a trusted Certificate Authority."
else
    echo "SSL certificates already exist."
fi

# Check running containers
echo "Checking Docker container status..."
docker ps

# Build the Docker image
echo "Building Docker image: $CONTAINER_NAME..."
docker build -t $CONTAINER_NAME .

# Run the Docker container with necessary configurations
echo "Deploying Docker container: $CONTAINER_NAME..."
docker run -d -p 8000:8000 -v $(pwd)/certs:/app/certs --env-file .env --restart always --name $CONTAINER_NAME $CONTAINER_NAME

# Check running containers again
echo "Checking Docker container status after deployment..."
docker ps

# Check container logs
echo "Fetching logs for container: $CONTAINER_NAME..."
docker logs $CONTAINER_NAME

# Wait for 20 seconds before checking API health
echo "Waiting for 20 seconds to allow API to start..."
sleep 20

# Check the API health status
echo "Checking API health status..."
curl -k https://localhost:8000/health

echo -e "\nFor accessing without the -k flag (ignore SSL warnings), add the self-signed certificate to your trusted certificates."