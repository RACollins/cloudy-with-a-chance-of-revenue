from typing import Any

import boto3


class S3Client:
    def __init__(self, bucket_name: str, *, client: Any | None = None) -> None:
        self.bucket_name = bucket_name
        self._client = client or boto3.client("s3")

    def put_text(self, key: str, content: str, content_type: str = "text/plain") -> str:
        self._client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content.encode("utf-8"),
            ContentType=content_type,
        )
        return f"s3://{self.bucket_name}/{key}"

    def put_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        self._client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"s3://{self.bucket_name}/{key}"

    def get_text(self, key: str) -> str:
        response = self._client.get_object(Bucket=self.bucket_name, Key=key)
        return response["Body"].read().decode("utf-8")

    def get_json(self, key: str) -> dict:
        import json

        return json.loads(self.get_text(key))
