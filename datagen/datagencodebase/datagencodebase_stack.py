from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_lambda as _lambda,
    Size,
)
# from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion

class DatagencodebaseStack(Stack):

    def __init__(self,
                 scope: Construct,
                 construct_id: str,

                 outputbucket: str,
                 schemabucket: str,
                 key: str,
                 datarequesttype: str,
                 inschema: str,
                 datarequestsize: str,

                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "DatagencodebaseQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "DatagencodebaseTopic"
        )

        role = iam.Role(
            self,
            'ServiceRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=('service-role/AWSLambdaBasicExecutionRole')),
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=('AmazonS3FullAccess'))
            ],
        )
        # faker_lambda_layer = PythonLayerVersion(
            # self, 'FakerLambdaLayer',
            # entry='python',
            # compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
            # description='Faker Library',
            # layer_version_name='FakerLambdaLayer'
       # )

        # Defines an AWS Lambda resource
        my_lambda = _lambda.Function(
            self, 'DataGenHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            # layers=[faker_lambda_layer],
            code=_lambda.Code.from_asset('lambda'),
            timeout=Duration.minutes(15),
            memory_size=5000,
            ephemeral_storage_size=Size.mebibytes(5000),
            role=role,
            # memory_size=Size.mebibytes(5000),
            environment={
                "BatchSize": "1000",
                "Key": key,
                "OutputBucket": outputbucket,
                "SchemaBucket": schemabucket,
                "DataRequestType" : datarequesttype,
                "InSchema": inschema,
                "DataRequestSize": datarequestsize
            },
            handler='DataGenCore.handler',
        )

        topic.add_subscription(subs.SqsSubscription(queue))
