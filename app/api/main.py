import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.config import settings
from app.domain.schemas import (
    ApproveMergeRequest,
    ForecastRequest,
    JobRecord,
    PreprocessRequest,
)
from app.lambdas.inference.handler import handler as inference_handler
from app.lambdas.preprocess.handler import handler as preprocess_handler
from app.lambdas.train_submit.handler import handler as train_submit_handler
from app.services.dynamodb_client import DynamoDBClient

app = FastAPI(title="Cloudy API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _invoke(handler, payload: dict) -> dict:
    import os

    os.environ.setdefault("DATA_BUCKET_NAME", settings.data_bucket_name)
    os.environ.setdefault("JOBS_TABLE_NAME", settings.jobs_table_name)
    os.environ.setdefault("SAGEMAKER_ROLE_ARN", settings.sagemaker_role_arn)
    os.environ.setdefault("TRAINING_IMAGE_URI", settings.training_image_uri)

    result = handler({"body": json.dumps(payload)}, None)
    body = json.loads(result["body"])
    if result["statusCode"] >= 400:
        raise HTTPException(status_code=result["statusCode"], detail=body)
    return body


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/preprocess")
def preprocess(request: PreprocessRequest) -> dict:
    return _invoke(preprocess_handler, request.model_dump(mode="json"))


@app.post("/approve-merge")
def approve_merge_route(request: ApproveMergeRequest) -> dict:
    return _invoke(train_submit_handler, request.model_dump())


@app.get("/status/{job_id}", response_model=JobRecord)
def get_status(job_id: str) -> JobRecord:
    db = DynamoDBClient(settings.jobs_table_name)
    try:
        return db.get_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/forecast")
def forecast(request: ForecastRequest) -> dict:
    return _invoke(inference_handler, request.model_dump())


def run() -> None:
    import uvicorn

    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)
