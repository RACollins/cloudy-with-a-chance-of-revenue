#!/usr/bin/env bash
set -euo pipefail
# Build and push training container to ECR (requires AWS credentials).
cd "$(dirname "$0")/.."
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
REGION="${AWS_REGION:-us-east-1}"
REPO="${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com/cloudy-training"
aws ecr get-login-password --region "$REGION" | docker login --username AWS --password-stdin "${ACCOUNT}.dkr.ecr.${REGION}.amazonaws.com"
docker build -f ml/training/Dockerfile -t cloudy-training .
docker tag cloudy-training:latest "${REPO}:latest"
docker push "${REPO}:latest"
