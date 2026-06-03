import json
import os

from app.domain.job_status import JobStatus
from app.services.dynamodb_client import DynamoDBClient
from app.services.job_transitions import mark_training_complete


def handler(event: dict, context: object) -> dict:
    """EventBridge handler for SageMaker training job terminal states."""
    detail = event.get("detail", {})
    status = detail.get("TrainingJobStatus", "")

    table = os.environ["JOBS_TABLE_NAME"]
    bucket = os.environ["DATA_BUCKET_NAME"]

    if status != "Completed":
        return {"statusCode": 200, "body": json.dumps({"skipped": True})}

    # Skeleton: derive job_id from hyperparameters or job name prefix.
    # Real implementation will parse SageMaker DescribeTrainingJob response.
    job_id = detail.get("HyperParameters", {}).get("job-id")
    if not job_id:
        return {"statusCode": 200, "body": json.dumps({"skipped": True, "reason": "no job-id"})}

    db = DynamoDBClient(table)
    model_path = f"s3://{bucket}/models/{job_id}/output/model.tar.gz"
    fi_path = f"s3://{bucket}/feature-importance/{job_id}.json"

    mark_training_complete(
        job_id,
        db=db,
        s3_model_path=model_path,
        s3_feature_importance_path=fi_path,
    )
    return {
        "statusCode": 200,
        "body": json.dumps({"job_id": job_id, "job_status": JobStatus.AWAITING_FORECAST_APPROVAL.value}),
    }
