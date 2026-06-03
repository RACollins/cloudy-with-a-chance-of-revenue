#!/usr/bin/env python3
import aws_cdk as cdk

from stacks.data_stack import DataStack
from stacks.compute_stack import ComputeStack
from stacks.api_stack import ApiStack

app = cdk.App()
env = cdk.Environment(
    account=app.node.try_get_context("account"),
    region=app.node.try_get_context("region") or "us-east-1",
)

data = DataStack(app, "CloudyDataStack", env=env)
compute = ComputeStack(
    app,
    "CloudyComputeStack",
    data_bucket=data.bucket,
    jobs_table=data.jobs_table,
    env=env,
)
ApiStack(
    app,
    "CloudyApiStack",
    preprocess_fn=compute.preprocess_fn,
    train_submit_fn=compute.train_submit_fn,
    inference_fn=compute.inference_fn,
    status_fn=compute.status_fn,
    env=env,
)

app.synth()
