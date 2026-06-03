import json
import os

from app.domain.schemas import ApproveMergeRequest
from app.services.dynamodb_client import DynamoDBClient
from app.services.job_transitions import JobTransitionError, approve_merge
from app.services.sagemaker_client import SageMakerClient


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict, context: object) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
        request = ApproveMergeRequest(**body)

        db = DynamoDBClient(os.environ["JOBS_TABLE_NAME"])
        sagemaker = SageMakerClient(
            role_arn=os.environ["SAGEMAKER_ROLE_ARN"],
            image_uri=os.environ["TRAINING_IMAGE_URI"],
            bucket_name=os.environ["DATA_BUCKET_NAME"],
        )
        training_job_name, status = approve_merge(
            request.job_id,
            db=db,
            sagemaker=sagemaker,
        )
        return _response(
            200,
            {
                "job_id": request.job_id,
                "job_status": status.value,
                "sagemaker_training_job_name": training_job_name,
            },
        )
    except JobTransitionError as exc:
        return _response(409, {"error": str(exc)})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
