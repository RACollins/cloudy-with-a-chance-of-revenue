import os
from pathlib import Path

from aws_cdk import (
    Duration,
    Stack,
    aws_ecr as ecr,
    aws_events as events,
    aws_events_targets as targets,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
)
from constructs import Construct

REPO_ROOT = Path(__file__).resolve().parents[3]


class ComputeStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        data_bucket: s3.Bucket,
        jobs_table: dynamodb.Table,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.training_repo = ecr.Repository(
            self,
            "TrainingRepo",
            repository_name="cloudy-training",
        )

        self.sagemaker_role = iam.Role(
            self,
            "SageMakerRole",
            assumed_by=iam.ServicePrincipal("sagemaker.amazonaws.com"),
        )
        data_bucket.grant_read_write(self.sagemaker_role)

        common_env = {
            "DATA_BUCKET_NAME": data_bucket.bucket_name,
            "JOBS_TABLE_NAME": jobs_table.table_name,
            "SAGEMAKER_ROLE_ARN": self.sagemaker_role.role_arn,
            "TRAINING_IMAGE_URI": self.training_repo.repository_uri + ":latest",
        }

        lambda_code = _lambda.Code.from_asset(str(REPO_ROOT), exclude=["infra/cdk/cdk.out", ".venv", ".git"])

        self.preprocess_fn = _lambda.Function(
            self,
            "PreprocessFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="app.lambdas.preprocess.handler.handler",
            code=lambda_code,
            timeout=Duration.minutes(5),
            memory_size=1024,
            environment=common_env,
        )

        self.train_submit_fn = _lambda.Function(
            self,
            "TrainSubmitFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="app.lambdas.train_submit.handler.handler",
            code=lambda_code,
            timeout=Duration.minutes(2),
            memory_size=512,
            environment=common_env,
        )

        self.inference_fn = _lambda.Function(
            self,
            "InferenceFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="app.lambdas.inference.handler.handler",
            code=lambda_code,
            timeout=Duration.minutes(5),
            memory_size=2048,
            environment=common_env,
        )


        self.status_fn = _lambda.Function(
            self,
            "StatusFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="app.lambdas.status.handler.handler",
            code=lambda_code,
            timeout=Duration.seconds(30),
            memory_size=256,
            environment=common_env,
        )
        jobs_table.grant_read_data(self.status_fn)

        self.training_complete_fn = _lambda.Function(
            self,
            "TrainingCompleteFn",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="app.lambdas.training_complete.handler.handler",
            code=lambda_code,
            timeout=Duration.minutes(1),
            memory_size=256,
            environment=common_env,
        )

        data_bucket.grant_read_write(self.preprocess_fn)
        data_bucket.grant_read_write(self.inference_fn)
        data_bucket.grant_read(self.train_submit_fn)
        jobs_table.grant_read_write_data(self.preprocess_fn)
        jobs_table.grant_read_write_data(self.train_submit_fn)
        jobs_table.grant_read_write_data(self.inference_fn)
        jobs_table.grant_read_write_data(self.training_complete_fn)

        self.train_submit_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["sagemaker:CreateTrainingJob", "sagemaker:DescribeTrainingJob"],
                resources=["*"],
            )
        )
        self.train_submit_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["iam:PassRole"],
                resources=[self.sagemaker_role.role_arn],
            )
        )

        rule = events.Rule(
            self,
            "SageMakerTrainingCompleteRule",
            event_pattern=events.EventPattern(
                source=["aws.sagemaker"],
                detail_type=["SageMaker Training Job State Change"],
                detail={"TrainingJobStatus": ["Completed", "Failed"]},
            ),
        )
        rule.add_target(targets.LambdaFunction(self.training_complete_fn))
