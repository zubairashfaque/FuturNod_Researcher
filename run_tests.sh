#!/bin/bash

# Script to run tests in the Docker container

echo "Running tests for FuturNod Researcher API"
echo "----------------------------------------"

# Check if the container is running
if ! docker ps | grep -q futurnod-researcher-api; then
    echo "Error: Container 'futurnod-researcher-api' is not running."
    echo "Please start the container before running tests."
    exit 1
fi

# Run the pytest command in the container
echo "Running tests in Docker container..."
docker exec -it futurnod-researcher-api pytest -v

# Add the option to run with coverage
if [ "$1" == "--cov" ]; then
    echo -e "\nRunning tests with coverage..."
    docker exec -it futurnod-researcher-api pytest --cov=. --cov-report=term
fi

# Add option to run specific test file
if [ -n "$2" ]; then
    echo -e "\nRunning specific test file: $2"
    docker exec -it futurnod-researcher-api pytest -v "$2"
fi

echo "----------------------------------------"
echo "Tests completed."