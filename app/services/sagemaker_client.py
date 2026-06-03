import os
from datetime import UTC, datetime
from typing import Any

import boto3


class SageMakerClient:
    def __init__(
        self,
        *,
        role_arn: str,
        image_uri: str,
        bucket_name: str,
        client: Any | None = None,
    ) -> None:
        self.role_arn = role_arn
        self.image_uri = image_uri
        self.bucket_name = bucket_name
        self._client = client or boto3.client("sagemaker")

    def submit_training_job(
        self,
        job_id: str,
        merged_s3_uri: str,
        output_prefix: str = "models",
    ) -> str:
        training_job_name = f"cloudy-{job_id[:8]}-{int(datetime.now(UTC).timestamp())}"
        output_path = f"s3://{self.bucket_name}/{output_prefix}/{job_id}/"

        self._client.create_training_job(
            TrainingJobName=training_job_name,
            AlgorithmSpecification={
                "TrainingImage": self.image_uri,
                "TrainingInputMode": "File",
            },
            RoleArn=self.role_arn,
            InputDataConfig=[
                {
                    "ChannelName": "training",
                    "DataSource": {
                        "S3DataSource": {
                            "S3DataType": "S3Prefix",
                            "S3Uri": merged_s3_uri,
                            "S3DataDistributionType": "FullyReplicated",
                        }
                    },
                    "ContentType": "text/csv",
                }
            ],
            OutputDataConfig={"S3OutputPath": output_path},
            ResourceConfig={
                "InstanceType": os.getenv("SAGEMAKER_INSTANCE_TYPE", "ml.m5.large"),
                "InstanceCount": 1,
                "VolumeSizeInGB": 30,
            },
            StoppingCondition={"MaxRuntimeInSeconds": 3600},
            HyperParameters={
                "job-id": job_id,
                "s3-bucket": self.bucket_name,
            },
        )
        return training_job_name
