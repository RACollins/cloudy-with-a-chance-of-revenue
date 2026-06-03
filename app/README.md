# App

- `domain/` — Pydantic schemas and job status enum
- `services/` — validation, weather merge, S3, DynamoDB, SageMaker
- `lambdas/` — preprocess, train_submit, inference, training_complete, status
- `api/` — local FastAPI BFF mirroring API Gateway routes
- `frontend/` — Streamlit multi-page UI with human-in-the-loop gates
