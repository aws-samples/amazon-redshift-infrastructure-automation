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
    aws_s3,
    custom_resources as cr
)
import boto3

region = boto3.session.Session().region_name
account = boto3.client('sts').get_caller_identity().get('Account')
s3 = boto3.resource('s3')

# noinspection PyTypeChecker
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
                #  outputfiletype: str,
                 batchsize: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        queue = sqs.Queue(
            self, "DatagencodebaseQueue",
            visibility_timeout=Duration.seconds(300),
        )

        topic = sns.Topic(
            self, "DatagencodebaseTopic"
        )

        source_bucket_name = 'aarete-poc'
        source_key = "testschema.json"
        destination_bucket_name = s3.Bucket('aarete-copy-test')
        destination_key = "testschema.json"

        copy_source = {'Bucket': source_bucket_name, 'Key': source_key}
        destination_bucket_name.copy(copy_source, destination_key)

        role = iam.Role(
            self,
            'ServiceRole',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    managed_policy_name='service-role/AWSLambdaBasicExecutionRole'),
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='AmazonS3FullAccess')
            ],
        )

        # Check for public bucket name and arn
        # iBucket = aws_s3.Bucket.from_bucket_arn(self, 'bucket',
        #                                         bucket_arn='arn:aws:s3:::airflow-bucket')

        # fakerlambdalayer = _lambda.LayerVersion(self, 'FakerLambdaLayer',
        #                                         layer_version_name='FakerLambdaLayer',
        #                                         code=_lambda.S3Code(iBucket, key='lambdalayer/faker.zip'),
        #                                         compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        #                                         license="none",
        #                                         description="A layer to test the L2 construct"
        #                                         )

        pandaslambdalayer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            id='AWSSDKPandas-Python39',
            layer_version_arn='arn:aws:lambda:us-east-1:336392948345:layer:AWSSDKPandas-Python39:10'
        )

        # Defines an AWS Lambda resource
        _lambda.Function(
            self, 'DataGenHandler',
            runtime=_lambda.Runtime.PYTHON_3_9,
            function_name='datagenfunction',
            # layers=[fakerlambdalayer, pandaslambdalayer],
            layers=[pandaslambdalayer],
            code=_lambda.Code.from_asset('lambda'),
            timeout=Duration.minutes(15),
            memory_size=5000,
            ephemeral_storage_size=Size.mebibytes(5000),
            role=role,
            environment={
                "BatchSize": "1000",
                "Key": key,
                "OutputBucket": outputbucket,
                "SchemaBucket": schemabucket,
                "DataRequestType": datarequesttype,
                "InSchema": inschema,
                "DataRequestSize": datarequestsize
                # "OutputFileType": outputfiletype
            },
            handler='DataGenCore.handler',
        )

        function_Arn = 'arn:aws:lambda:' + region + ':' + account + ':function:datagenfunction'

        cr.AwsCustomResource(
            scope=self,
            id="invoke_lambda",
            policy=(
                cr.AwsCustomResourcePolicy.from_statements(
                    statements=[
                        iam.PolicyStatement(
                            actions=["lambda:InvokeFunction"],
                            effect=iam.Effect.ALLOW,
                            resources=[function_Arn],
                        )
                    ]
                )
            ),
            timeout=Duration.minutes(15),
            on_create=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": 'datagenfunction',
                    "InvocationType": "Event",
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    "JobSenderTriggerPhysicalId"
                ),
            ),
            on_update=cr.AwsSdkCall(
                service="Lambda",
                action="invoke",
                parameters={
                    "FunctionName": 'datagenfunction',
                    "InvocationType": "Event",
                },
                physical_resource_id=cr.PhysicalResourceId.of(
                    "JobSenderTriggerPhysicalId"
                ),
            ),
        )

        topic.add_subscription(subs.SqsSubscription(queue))
