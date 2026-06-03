import json
import os

from app.services.dynamodb_client import DynamoDBClient


def handler(event: dict, context: object) -> dict:
    job_id = event.get("pathParameters", {}).get("job_id")
    if not job_id:
        return {"statusCode": 400, "body": json.dumps({"error": "job_id required"})}

    db = DynamoDBClient(os.environ["JOBS_TABLE_NAME"])
    try:
        job = db.get_job(job_id)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(job.model_dump(mode="json")),
        }
    except KeyError:
        return {"statusCode": 404, "body": json.dumps({"error": f"Job not found: {job_id}"})}
