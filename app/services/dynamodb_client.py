from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

import boto3
from boto3.dynamodb.conditions import Attr

from app.domain.job_status import JobStatus
from app.domain.schemas import JobRecord, UserMetadata, ValidationSummary


def _serialize(value: Any) -> Any:
    if isinstance(value, float):
        return Decimal(str(value))
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_serialize(v) for v in value]
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def _deserialize(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value) if value % 1 else int(value)
    if isinstance(value, dict):
        return {k: _deserialize(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_deserialize(v) for v in value]
    return value


class DynamoDBClient:
    def __init__(self, table_name: str, *, resource: Any | None = None) -> None:
        self.table_name = table_name
        self._resource = resource or boto3.resource("dynamodb")
        self._table = self._resource.Table(table_name)

    def create_job(
        self,
        job_id: str,
        user_metadata: UserMetadata,
        *,
        s3_raw_path: str,
        s3_merged_path: str,
        validation_summary: ValidationSummary,
        job_status: JobStatus = JobStatus.AWAITING_MERGE_APPROVAL,
    ) -> JobRecord:
        now = datetime.now(UTC)
        item = {
            "job_id": job_id,
            "job_status": job_status.value,
            "user_metadata": _serialize(user_metadata.model_dump()),
            "s3_raw_path": s3_raw_path,
            "s3_merged_path": s3_merged_path,
            "validation_summary": _serialize(validation_summary.model_dump()),
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }
        self._table.put_item(Item=item)
        return self.get_job(job_id)

    def get_job(self, job_id: str) -> JobRecord:
        response = self._table.get_item(Key={"job_id": job_id})
        if "Item" not in response:
            raise KeyError(f"Job not found: {job_id}")
        item = _deserialize(response["Item"])
        if item.get("validation_summary"):
            item["validation_summary"] = ValidationSummary(**item["validation_summary"])
        item["user_metadata"] = UserMetadata(**item["user_metadata"])
        for field in ("merge_approved_at", "forecast_approved_at", "created_at", "updated_at"):
            if item.get(field):
                item[field] = datetime.fromisoformat(item[field])
        item["job_status"] = JobStatus(item["job_status"])
        return JobRecord(**item)

    def update_status(
        self,
        job_id: str,
        *,
        expected_status: JobStatus | None = None,
        new_status: JobStatus,
        extra: dict[str, Any] | None = None,
    ) -> JobRecord:
        now = datetime.now(UTC)
        update_parts = ["job_status = :status", "updated_at = :updated_at"]
        values: dict[str, Any] = {
            ":status": new_status.value,
            ":updated_at": now.isoformat(),
        }
        if extra:
            for idx, (key, val) in enumerate(extra.items()):
                placeholder = f":extra{idx}"
                update_parts.append(f"{key} = {placeholder}")
                values[placeholder] = _serialize(val)

        kwargs: dict[str, Any] = {
            "Key": {"job_id": job_id},
            "UpdateExpression": "SET " + ", ".join(update_parts),
            "ExpressionAttributeValues": values,
            "ReturnValues": "ALL_NEW",
        }
        if expected_status is not None:
            kwargs["ConditionExpression"] = Attr("job_status").eq(expected_status.value)

        response = self._table.update_item(**kwargs)
        item = _deserialize(response["Attributes"])
        if item.get("validation_summary"):
            item["validation_summary"] = ValidationSummary(**item["validation_summary"])
        item["user_metadata"] = UserMetadata(**item["user_metadata"])
        for field in ("merge_approved_at", "forecast_approved_at", "created_at", "updated_at"):
            if item.get(field):
                item[field] = datetime.fromisoformat(item[field])
        item["job_status"] = JobStatus(item["job_status"])
        return JobRecord(**item)
