from aws_cdk import Stack, aws_apigatewayv2 as apigwv2, aws_lambda as _lambda
from aws_cdk.aws_apigatewayv2_integrations import HttpLambdaIntegration
from constructs import Construct


class ApiStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        *,
        preprocess_fn: _lambda.Function,
        train_submit_fn: _lambda.Function,
        inference_fn: _lambda.Function,
        status_fn: _lambda.Function,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        http_api = apigwv2.HttpApi(self, "CloudyHttpApi")

        http_api.add_routes(
            path="/preprocess",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration("PreprocessIntegration", preprocess_fn),
        )
        http_api.add_routes(
            path="/approve-merge",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration("TrainSubmitIntegration", train_submit_fn),
        )
        http_api.add_routes(
            path="/status/{job_id}",
            methods=[apigwv2.HttpMethod.GET],
            integration=HttpLambdaIntegration("StatusIntegration", status_fn),
        )
        http_api.add_routes(
            path="/forecast",
            methods=[apigwv2.HttpMethod.POST],
            integration=HttpLambdaIntegration("InferenceIntegration", inference_fn),
        )
