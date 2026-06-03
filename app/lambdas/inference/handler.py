import json
import os
from datetime import UTC, datetime, timedelta

from app.domain.job_status import JobStatus
from app.domain.schemas import ForecastRequest, ForecastResponse
from app.services.dynamodb_client import DynamoDBClient
from app.services.job_transitions import JobTransitionError, approve_forecast
from app.services.s3_client import S3Client


def _response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _stub_forecast(horizon: int) -> list[dict]:
    start = datetime.now(UTC).date()
    return [
        {
            "timestamp": (start + timedelta(days=i)).isoformat(),
            "prediction": float(100 + i),
        }
        for i in range(1, horizon + 1)
    ]


def handler(event: dict, context: object) -> dict:
    bucket = os.environ["DATA_BUCKET_NAME"]
    table = os.environ["JOBS_TABLE_NAME"]

    try:
        body = json.loads(event.get("body") or "{}")
        request = ForecastRequest(**body)

        db = DynamoDBClient(table)
        approve_forecast(request.job_id, db=db)

        forecast = _stub_forecast(request.horizon)
        s3 = S3Client(bucket)
        forecast_key = f"forecasts/{request.job_id}.json"
        s3.put_text(forecast_key, json.dumps({"forecast": forecast}))

        db.update_status(
            request.job_id,
            expected_status=JobStatus.FORECASTING,
            new_status=JobStatus.COMPLETED,
            extra={"s3_forecast_path": f"s3://{bucket}/{forecast_key}"},
        )

        response = ForecastResponse(
            job_id=request.job_id,
            job_status=JobStatus.COMPLETED,
            forecast=forecast,
        )
        return _response(200, response.model_dump(mode="json"))
    except JobTransitionError as exc:
        return _response(409, {"error": str(exc)})
    except Exception as exc:
        return _response(500, {"error": str(exc)})
