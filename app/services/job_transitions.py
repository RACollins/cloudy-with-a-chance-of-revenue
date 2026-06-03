from datetime import UTC, datetime

from botocore.exceptions import ClientError

from app.domain.job_status import JobStatus
from app.services.dynamodb_client import DynamoDBClient
from app.services.sagemaker_client import SageMakerClient


class JobTransitionError(Exception):
    pass


def approve_merge(
    job_id: str,
    *,
    db: DynamoDBClient,
    sagemaker: SageMakerClient,
) -> tuple[str, JobStatus]:
    try:
        job = db.get_job(job_id)
        training_job_name = sagemaker.submit_training_job(
            job_id=job_id,
            merged_s3_uri=job.s3_merged_path or "",
        )
        db.update_status(
            job_id,
            expected_status=JobStatus.AWAITING_MERGE_APPROVAL,
            new_status=JobStatus.TRAINING,
            extra={
                "merge_approved_at": datetime.now(UTC).isoformat(),
                "sagemaker_training_job_name": training_job_name,
            },
        )
        return training_job_name, JobStatus.TRAINING
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise JobTransitionError(
                f"Job {job_id} is not awaiting merge approval"
            ) from exc
        raise


def approve_forecast(job_id: str, *, db: DynamoDBClient) -> JobStatus:
    try:
        db.update_status(
            job_id,
            expected_status=JobStatus.AWAITING_FORECAST_APPROVAL,
            new_status=JobStatus.FORECASTING,
            extra={"forecast_approved_at": datetime.now(UTC).isoformat()},
        )
        return JobStatus.FORECASTING
    except ClientError as exc:
        if exc.response["Error"]["Code"] == "ConditionalCheckFailedException":
            raise JobTransitionError(
                f"Job {job_id} is not awaiting forecast approval"
            ) from exc
        raise


def mark_training_complete(
    job_id: str,
    *,
    db: DynamoDBClient,
    s3_model_path: str,
    s3_feature_importance_path: str,
) -> JobStatus:
    db.update_status(
        job_id,
        expected_status=JobStatus.TRAINING,
        new_status=JobStatus.AWAITING_FORECAST_APPROVAL,
        extra={
            "s3_model_path": s3_model_path,
            "s3_feature_importance_path": s3_feature_importance_path,
        },
    )
    return JobStatus.AWAITING_FORECAST_APPROVAL
