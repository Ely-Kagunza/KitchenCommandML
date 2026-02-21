#!/bin/bash

# Deployment script for ML Service

set -e

echo "================================"
echo "ML Service Deployment Script"
echo "================================"

# Configuration
ENVIRONMENT=${1:-production}
DOCKER_REGISTRY=${DOCKER_REGISTRY:-docker.io}
IMAGE_NAME=restaurant-ml-service
IMAGE_TAG=$(date +%Y%m%d_%H%M%S)

echo "Environment: $ENVIRONMENT"
echo "Image: $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG"

# Build Docker image
echo ""
echo "Building Docker image..."
docker build -t $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG \
             -t $DOCKER_REGISTRY/$IMAGE_NAME:latest \
             -f docker/Dockerfile .

# Push to registry
if [ "$ENVIRONMENT" = "production" ]; then
    echo ""
    echo "Pushing to registry..."
    docker push $DOCKER_REGISTRY/$IMAGE_NAME:$IMAGE_TAG
    docker push $DOCKER_REGISTRY/$IMAGE_NAME:latest
fi

# Deploy with docker-compose
echo ""
echo "Deploying with docker-compose..."
docker-compose -f docker/docker-compose.yml up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
sleep 10

# Check health
echo ""
echo "Checking service health..."
curl -f http://localhost:8000/api/health || {
    echo "Health check failed!"
    exit 1
}

echo ""
echo "================================"
echo "Deployment Complete!"
echo "================================"
echo ""
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/api/docs"
echo "Prometheus: http://localhost:9090"
echo "Grafana: http://localhost:3000"
