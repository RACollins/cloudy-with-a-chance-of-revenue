# Infrastructure (AWS CDK)

Three stacks:

1. **CloudyDataStack** — S3 bucket (raw/ 24h lifecycle), DynamoDB jobs table
2. **CloudyComputeStack** — Lambdas, SageMaker IAM role, ECR repo, EventBridge rule
3. **CloudyApiStack** — HTTP API Gateway routes

Deploy:

```bash
./scripts/deploy_infra.sh
```
