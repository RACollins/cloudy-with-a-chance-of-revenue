import json
import os
import uuid

from app.domain.job_status import JobStatus
from app.domain.schemas import PreprocessRequest, UserMetadata
from app.services.dynamodb_client import DynamoDBClient
from app.services.merge import merge_weather
from app.services.s3_client import S3Client
from app.services.validation import ValidationError, validate_csv


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def handler(event: dict, context: object) -> dict:
    bucket = os.environ["DATA_BUCKET_NAME"]
    table = os.environ["JOBS_TABLE_NAME"]

    try:
        if event.get("isBase64Encoded"):
            import base64
            raw_body = base64.b64decode(event["body"]).decode("utf-8")
        else:
            raw_body = event.get("body") or "{}"

        payload = json.loads(raw_body)
        request = PreprocessRequest(
            user_metadata=UserMetadata(**payload["user_metadata"]),
            csv_content=payload["csv_content"],
            datetime_column=payload.get("datetime_column", "timestamp"),
            target_column=payload.get("target_column", "value"),
        )

        job_id = str(uuid.uuid4())
        result = validate_csv(
            request.csv_content,
            request.datetime_column,
            request.target_column,
        )
        merged_df, summary = merge_weather(
            result.dataframe,
            result.summary,
            request.user_metadata.location_lat,
            request.user_metadata.location_lon,
        )

        s3 = S3Client(bucket)
        raw_key = f"raw/{job_id}.csv"
        merged_key = f"merged/{job_id}.csv"
        s3.put_text(raw_key, request.csv_content, content_type="text/csv")
        s3.put_text(
            merged_key,
            merged_df.to_csv(index=False),
            content_type="text/csv",
        )

        db = DynamoDBClient(table)
        db.create_job(
            job_id,
            request.user_metadata,
            s3_raw_path=f"s3://{bucket}/{raw_key}",
            s3_merged_path=f"s3://{bucket}/{merged_key}",
            validation_summary=summary,
            job_status=JobStatus.AWAITING_MERGE_APPROVAL,
        )

        return _response(
            200,
            {
                "job_id": job_id,
                "job_status": JobStatus.AWAITING_MERGE_APPROVAL.value,
                "validation_summary": summary.model_dump(),
            },
        )
    except ValidationError as exc:
        return _response(400, {"error": str(exc)})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
