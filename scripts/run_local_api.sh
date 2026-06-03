#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export DATA_BUCKET_NAME="${DATA_BUCKET_NAME:-local-bucket}"
export JOBS_TABLE_NAME="${JOBS_TABLE_NAME:-cloudy-jobs}"
export SAGEMAKER_ROLE_ARN="${SAGEMAKER_ROLE_ARN:-arn:aws:iam::000000000000:role/sagemaker}"
export TRAINING_IMAGE_URI="${TRAINING_IMAGE_URI:-000000000000.dkr.ecr.us-east-1.amazonaws.com/cloudy-training:latest}"
uv run cloudy-api
